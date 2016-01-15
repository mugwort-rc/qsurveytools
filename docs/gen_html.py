#!/usr/bin/env python

import sys
import argparse

import os
import fnmatch

BASEDIR = os.path.dirname(__file__)

# http://stackoverflow.com/questions/6987123/search-in-wildcard-folders-recursively-in-python
def locate(pattern, root_path):
    for path, dirs, files in os.walk(root_path):
        for filename in fnmatch.filter(files, pattern):
            yield path, filename

def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default=os.path.join(BASEDIR, 'md/'))
    parser.add_argument('--output', default=os.path.join(BASEDIR, 'html/html/'))
    args, unknown = parser.parse_known_args(args)

    if not os.path.isdir(args.input):
        print('input: "{}" is not directory.'.format(args.input))
        return 1
    if not os.path.isdir(args.output):
        print('output: "{}" is not directory.'.format(args.output))
        return 1

    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(os.path.join(BASEDIR, 'templates'), encoding='utf8'))
    tpl = env.get_template('template.html')
    import markdown
    from markdown.extensions.headerid import HeaderIdExtension
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.attr_list',
            HeaderIdExtension(forceid=False),
            'markdown.extensions.toc',
            "markdown.extensions.meta",
        ]
    )
    for path, file in locate('*.md', args.input):
        data = open(os.path.join(path, file)).read().decode('utf-8')
        html = tpl.render({
            'html': md.convert(data),
            "meta": md.Meta if hasattr(md, "Meta") else {},
        })
        distpath = args.output + path[len(args.input):]
        open(os.path.join(distpath, file[:-2]+'html'), 'w').write(html.encode('utf-8'))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))