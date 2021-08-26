

import shutil, os

def replace_res(filename, search_text, replace_text):
    dir = os.path.dirname(filename)
    newfile = os.path.join(dir, 'new_file')
    with open(filename, 'r') as rf:
        with open(newfile, 'w') as wf:
            for line in rf.readlines():
                if line.startswith(search_text):
                    print(line)
                    wf.write(replace_text)
                else:
                    wf.write(line)
    os.remove(filename)
    dir = os.path.dirname(filename)
    shutil.move(newfile, filename)
                

def strings(w, h):
    replace_res(
        './public/index.html',
        '        <video id="live"',
        f'        <video id="live" width="{w}" height="{h}" autoplay></video>\n'
        )

    replace_res(
        './public/static/scripts/constants.js',
        'var resolutions = [[',
        f'var resolutions = [[{w},{h}],[1280,720]],\n'
        )

    replace_res(
        './public/static/scripts/init_screen.js',
        '        canvas.width =',
        f'        canvas.width = {w}; canvas.height = {h};\n'
        )


if __name__ == '__main__':
    strings(1280, 720)
