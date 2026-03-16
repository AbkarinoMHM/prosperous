#!/usr/bin/env python3
import os, sys, subprocess, shutil, getpass
import kleipack

is_n0body = (getpass.getuser() == 'n0body')

SAVE_DIR = 'save'
BUILD_DIR = 'build'

def save_path(path):
    return os.path.join(SAVE_DIR, path)
def build_path(path):
    return os.path.join(BUILD_DIR, path)

SAVE_SK = save_path('SAVE.bin')
SAVE_input = save_path('SAVE')
SAVE_dec = build_path('SAVE_dec')
SAVE_inject = build_path('SAVE_inject')
SAVE_enc = build_path('SAVE_inject_enc')
SAVE_enc_rep = build_path('SAVE_inject_enc_rep')
SAVE_FILE_TO_INJECT = build_path('survival_1')

def clean():
    shutil.rmtree(BUILD_DIR, ignore_errors=True)

def install():
    # copy to usb drive
    shutil.copyfile(SAVE_enc_rep, 'i:/PS4/SAVEDATA/<YOUR_USER_ID>/CUSA00158/SAVE')

def ps5tool(cmd, sealedkey_path, path_in, path_out):
    subprocess.run(['ps5tool', cmd, '-k', sealedkey_path, '-o', path_out, path_in])

def inject(template_path, payload_path, output_path):
    template = open(template_path, 'rb').read()
    payload  = open(payload_path, 'rb').read() + b'\0'*256

    open(output_path, 'wb').write(
        template[:0x158000] + payload + template[0x158000+len(payload):])

def build():
    os.makedirs('build', exist_ok=True)

    lua_code = open('save_hax/code.lua', 'rb').read()
    savegame = open('save_hax/survival_1.lua', 'rb').read().replace(b'LUA_CODE_COOKIE', lua_code)
    open(SAVE_FILE_TO_INJECT, 'wb').write(kleipack.pack(savegame))

    ps5tool('decrypt', SAVE_SK, SAVE_input, SAVE_dec)
    inject(SAVE_dec, SAVE_FILE_TO_INJECT, SAVE_inject)
    ps5tool('encrypt', SAVE_SK, SAVE_inject, SAVE_enc)
    ps5tool('repair', SAVE_SK, SAVE_enc, SAVE_enc_rep)

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    if cmd == 'clean':
        clean()
    elif cmd == 'install':
        install()
    else:
        build()
