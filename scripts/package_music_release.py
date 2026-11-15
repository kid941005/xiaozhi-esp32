"""Package a built board ZIP plus the NAS service into release archives.

Usage:
  python scripts/package_music_release.py \
      --firmware releases/v2.6.0_bread-compact-wifi-music.zip \
      --version v0.2.0 --board bread-compact-wifi
"""
import argparse
import hashlib
from pathlib import Path
import zipfile

NOTICES = ['LICENSE', 'THIRD_PARTY_NOTICES.md', 'README.md', 'MUSIC_SETUP.md', 'RELEASE_NOTES.md']


def _nas_files(nas_dir: Path) -> list[Path]:
    keep = {'.env.example', 'Dockerfile', 'compose.yaml'}
    out = []
    for path in sorted(nas_dir.iterdir()):
        if not path.is_file():
            continue
        if path.name in keep or path.suffix in {'.py', '.txt', '.md', '.yaml', '.yml'}:
            out.append(path)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--firmware', required=True,
                        help='built board ZIP containing merged-binary.bin')
    parser.add_argument('--version', default='v0.2.0', help='release version tag')
    parser.add_argument('--board', default='bread-compact-wifi', help='board/variant slug')
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    out = root / 'releases'
    firmware = Path(args.firmware)
    if not firmware.is_absolute():
        firmware = root / firmware
    if not firmware.is_file():
        raise SystemExit(f'firmware ZIP not found: {firmware}')
    out.mkdir(exist_ok=True)

    fw_out = out / f'xiaozhi-music-{args.version}-{args.board}.zip'
    nas_out = out / f'xiaozhi-music-{args.version}-nas.zip'

    with zipfile.ZipFile(firmware) as src, zipfile.ZipFile(fw_out, 'w', zipfile.ZIP_DEFLATED) as dst:
        assert src.testzip() is None
        assert 'merged-binary.bin' in src.namelist()
        for name in src.namelist():
            dst.writestr(name, src.read(name))
        for name in NOTICES:
            if (root / name).is_file():
                dst.write(root / name, name)

    nas_dir = root / 'nas-music'
    with zipfile.ZipFile(nas_out, 'w', zipfile.ZIP_DEFLATED) as dst:
        for path in _nas_files(nas_dir):
            dst.write(path, 'nas-music/' + path.name)
        for name in NOTICES:
            if (root / name).is_file():
                dst.write(root / name, name)

    lines = []
    for path in (fw_out, nas_out):
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
        lines.append(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name)
    (out / 'SHA256SUMS.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('Packaged and verified firmware/NAS ZIPs; wrote SHA256SUMS.txt')


if __name__ == '__main__':
    main()
