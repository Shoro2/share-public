# network — ByteBuffer

> The serialization primitive every wire packet builds on: a growable byte vector with typed `<<`/`>>` operators, separate read/write cursors, and an exception family that signals over-read or invalid data. `WorldPacket` (see [`02-worldpacket.md`](./02-worldpacket.md)) is just `ByteBuffer + opcode`.

## Critical files

| File | Role |
|---|---|
| `src/server/shared/Packets/ByteBuffer.h:69` | `class ByteBuffer` declaration |
| `src/server/shared/Packets/ByteBuffer.h:72` | `static constexpr DEFAULT_SIZE = 0x1000` (4 KiB) — initial reserve |
| `src/server/shared/Packets/ByteBuffer.h:31` | `class ByteBufferException` (root) |
| `src/server/shared/Packets/ByteBuffer.h:45` | `class ByteBufferPositionException` (over-read / over-put) |
| `src/server/shared/Packets/ByteBuffer.h:53` | `class ByteBufferSourceException` (NULL src or zero-sized append) |
| `src/server/shared/Packets/ByteBuffer.h:61` | `class ByteBufferInvalidValueException` (NaN float / non-UTF-8 string) |
| `src/server/shared/Packets/ByteBuffer.h:128` | `template<T> void append(T)` — endian-converts then appends |
| `src/server/shared/Packets/ByteBuffer.h:144`–`231` | `operator<<` overloads for `bool`, `uint8`–`uint64`, `int8`–`int64`, `float`, `double`, `string_view`, `string`, `char const*` |
| `src/server/shared/Packets/ByteBuffer.h:233`–`295` | `operator>>` overloads (mirror set; `>>` on `bool` reads a `char`, NUL-terminated for `string`) |
| `src/server/shared/Packets/ByteBuffer.h:351` | `template<T> T read()` (advances `_rpos`) |
| `src/server/shared/Packets/ByteBuffer.h:358` | `T read(pos) const` (random-access read with bounds check) |
| `src/server/shared/Packets/ByteBuffer.h:387` | `void readPackGUID(uint64&)` — WoW packed-GUID decoding |
| `src/server/shared/Packets/ByteBuffer.h:415` | `std::string ReadCString(bool requireValidUtf8 = true)` |
| `src/server/shared/Packets/ByteBuffer.h:494` | `void appendPackXYZ(float, float, float)` — `MSG_MOVE`-style packed coordinate |
| `src/server/shared/Packets/ByteBuffer.h:503` | `void appendPackGUID(uint64)` |
| `src/server/shared/Packets/ByteBuffer.h:524` | `void AppendPackedTime(time_t)` (calendar / mail timestamps) |
| `src/server/shared/Packets/ByteBuffer.h:525` | `void put(pos, src, cnt)` — overwrite range without moving `_wpos` |
| `src/server/shared/Packets/ByteBuffer.cpp:30` | `ByteBufferPositionException::ByteBufferPositionException` (formats message) |
| `src/server/shared/Packets/ByteBuffer.cpp:77` | `ReadCString` impl (UTF-8 validated via `utf8::is_valid`) |
| `src/server/shared/Packets/ByteBuffer.cpp:110` | `append(uint8 const*, std::size_t)` — the only re-allocator (custom growth tiers) |

## Key concepts

- **Two cursors** — `_rpos` (read) and `_wpos` (write) are independent `std::size_t` indices into `_storage` (`std::vector<uint8>`). Resetting both at once is `clear()`.
- **Endian conversion** — every typed `append` / `read` runs `EndianConvert` (`ByteConverter.h`); on little-endian hosts (the supported configuration) this is a no-op, so values land in WoW wire order.
- **`append(T)` vs `put(pos, T)`** — `append` advances `_wpos`; `put` does not. `put` is used to backfill a header field whose value is computed after the body is serialized (e.g., a length prefix).
- **Custom growth tiers** (`ByteBuffer.cpp:120`) — when the destination size is `<100`, reserve 300; `<750` → 2500; `<6000` → 10000; otherwise 400000. Designed for the typical opcode size distribution. `ASSERT(size() < 10'000'000)` guards against runaway buffers.
- **`readPackGUID` / `appendPackGUID`** — WoW packs an 8-byte GUID by sending one mask byte that flags which of the 8 bytes are non-zero, then those bytes only. Used everywhere a GUID appears in a packet.
- **No bit-stream API** — unlike Cataclysm-and-later cores, the WotLK `ByteBuffer` does **not** have `WriteBit`/`WriteBits`/`FlushBits`. All wire fields are byte-aligned.
- **Floats are validated on read** — `operator>>(float&)` and `operator>>(double&)` throw `ByteBufferInvalidValueException` if the parsed value is non-finite (`!std::isfinite`). Callers must therefore catch this when consuming client packets.
- **String reads are UTF-8 validated by default** — `ReadCString(true)` throws `ByteBufferInvalidValueException("string", ...)` on the first invalid sequence. Pass `false` only for fields whose content is opaque bytes.

## Flow / data shape

Layout invariant: `0 ≤ _rpos ≤ _wpos ≤ _storage.size()`.

```
_storage:  [b0][b1][b2][b3][b4][b5][b6][b7]…[b_{wpos-1}] | unused | … capacity …
                              ^                          ^
                              _rpos                      _wpos
            <─── already read ───>< ── still readable ──><──   appendable  ──>
```

Typical write/read sequence:

```cpp
ByteBuffer buf;                       // reserves DEFAULT_SIZE (4 KiB)
buf << uint32(0xCAFEBABE);            // append 4 bytes; _wpos = 4
buf << "Hello";                       // append 5 chars + NUL; _wpos = 10
buf.append<uint8>(0xFF);              // template form; same effect as <<

uint32 magic;
std::string greeting;
buf >> magic >> greeting;             // _rpos walks 0 → 4 → 10
ASSERT(magic == 0xCAFEBABE);
```

Backfill with `put`:

```cpp
auto sizePos = buf.wpos();            // remember slot
buf << uint16(0);                     // placeholder
buf << uint64(playerGuid) << uint32(payload);
uint16 size = uint16(buf.wpos() - sizePos - sizeof(uint16));
buf.put<uint16>(sizePos, size);       // overwrite without moving _wpos
```

Throw conditions (call-sites must `try`/`catch ByteBufferException const&`):

| Condition | Type thrown | Where |
|---|---|---|
| Read past `size()` | `ByteBufferPositionException` | `read<T>(pos)` (`:362`), `read(uint8*, len)` (`:374`), `operator[]` (`:301`), `read_skip` (`:345`) |
| `append(NULL, …)` | `ByteBufferSourceException` | `append(uint8 const*, std::size_t)` (`.cpp:112`) |
| Non-finite float | `ByteBufferInvalidValueException("float", …)` | `operator>>(float&)` (`.cpp:62`) |
| Non-UTF-8 string | `ByteBufferInvalidValueException("string", …)` | `ReadCString` (`.cpp:90`) |

`WorldSession::Update` already wraps each handler dispatch in a `catch (ByteBufferException const&)` block (`WorldSession.cpp:513`) — handlers may simply throw out of the bottom on a malformed packet.

## Hooks & extension points

—  `ByteBuffer` is a low-level primitive. There is no `ScriptMgr` hook. Module code uses it directly via `WorldPacket`. To trace bytes for debugging, see `print_storage()` / `textlike()` / `hexlike()` (`.cpp:152`–`221`); they emit to log category `network.opcode.buffer` at TRACE level only.

## Cross-references

- Engine-side: [`02-worldpacket.md`](./02-worldpacket.md) (the opcode-bearing subclass), [`04-worldsocket.md`](./04-worldsocket.md) (where `ByteBuffer` meets the wire), [`03-opcodes.md`](./03-opcodes.md) (whose handlers do the typed reads).
- Project-side: [`../../02-architecture.md`](../../02-architecture.md) (top-level layout — `ByteBuffer` lives in `src/server/shared/Packets`, *not* under `common/`).
- External: Doxygen `classByteBuffer`, `classByteBufferException`, `classByteBufferPositionException`, `ByteBuffer_8h`.
