"""Build WoW-compatible transparent TGA sprite sheets and OGG audio."""
import pathlib
import struct
import subprocess
import sys

root = pathlib.Path(__file__).resolve().parents[1]
source = pathlib.Path(sys.argv[1]).expanduser()
destination = root / "ClappingCat" / "Media"
destination.mkdir(parents=True, exist_ok=True)
fps, cell, grid = 15, 256, 4
raw = subprocess.check_output([
    "ffmpeg", "-v", "error", "-i", str(source), "-an", "-vf",
    "fps=15,crop=1080:1440:0:240,scale=192:256,pad=256:256:32:0:color=black@0,format=bgra",
    "-f", "rawvideo", "pipe:1",
])
frame_bytes = cell * cell * 4
assert len(raw) % frame_bytes == 0
count = len(raw) // frame_bytes
side = cell * grid
for first in range(0, count, grid * grid):
    sheet = bytearray(side * side * 4)
    for index in range(first, min(first + grid * grid, count)):
        local = index - first
        x, y = local % grid * cell, local // grid * cell
        for row in range(cell):
            start = index * frame_bytes + row * cell * 4
            target = ((y + row) * side + x) * 4
            sheet[target:target + cell * 4] = raw[start:start + cell * 4]
    # Uncompressed, top-left origin, 32-bit BGRA with eight alpha bits.
    header = struct.pack("<BBBHHBHHHHBB", 0, 0, 2, 0, 0, 0, 0, 0, side, side, 32, 0x28)
    (destination / f"Cat{first // 16 + 1:02d}.tga").write_bytes(header + sheet)
for volume in range(5, 101, 5):
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(source), "-vn",
        "-af", f"volume={volume / 100}", "-c:a", "libvorbis", "-q:a", "4",
        str(destination / f"Clap{volume:03d}.ogg"),
    ], check=True)
old_audio = destination / "Clap.ogg"
if old_audio.exists():
    old_audio.unlink()
(root / "ClappingCat" / "Media.lua").write_text(
    f"local _, addon = ...\naddon.media = {{ fps = {fps}, frames = {count}, columns = {grid}, rows = {grid} }}\n"
)
print(f"Built {count} frames in {(count + 15) // 16} sheets, plus 20 volume variants.")
