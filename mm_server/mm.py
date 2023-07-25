from flask import Flask, request, jsonify
from mm_server import app
import sftp_mech as sftpm

doer = sftpm.sftp_doer


@app.route('/info')
def info():
    resp = {
        'connecting_ip': request.headers['X-Real-IP'],
        'proxy_ip': request.headers['X-Forwarded-For'],
        'host': request.headers['Host'],
        'user-agent': request.headers['User-Agent']
    }
    return jsonify(resp)


@app.route('/content')
def content_view():
    doer.xch_dir('/content')

    blob = tag_list(tuple(i for i in sftpm.sftp_doer.xls_blunt()), True)

    page = print_html(blob, 'Home')

    return page


@app.route('/media')
def media_view():
    doer.xch_dir('/content/media')
    blob = tag_list(tuple(i for i in sftpm.sftp_doer.xls_blunt()), True)

    page = print_html(blob, 'Media')

    return page


@app.route('/books')
def books_view():
    doer.xch_dir(doer.nvr.move('/content/media/books'))

    # tag_link = lambda x: f'<a href="{doer.nvr.getprev() + "/" + x}">{x}</a>'
    # tag_li = lambda x: "<ul>" + ("".join("<li>" + tag_link(str(i)) + "</li>" for i in x)) + "</ul>"

    # blob = "\n".join(tag_link(i) for i in sftpm.sftp_doer.xls_blunt())
    blob = tag_list(tuple(i for i in sftpm.sftp_doer.xls_blunt()), True, '/books')

    page = print_html(blob, 'Books')

    return page


@app.route('/tv')
def tv_view():
    doer.xch_dir('/content/media/tv')

    blob = tag_list(tuple(i for i in sftpm.sftp_doer.xls_blunt()), True, '/tv')

    page = print_html(blob, 'Tv')

    return page


def tag_link(item: str, prefix: str = None):
    return '<a href="' \
        + (str('/' + item) if prefix is None else (str(prefix+item))) + '">' + item + '</a>'


def tag_list(items: tuple, add_linktag: bool = True, prefix: str = None):
    return '<ul>' + ('\n'.join(tuple((lambda i: '<li>'
                                                + (tag_link(i, prefix) if add_linktag else i)
                                                + '</li>')(i) for i in items))) + '</ul>'


def print_html(content, title):
    blob = [str("<h1>"+title+"</h1>"), ]
    blob.append("<br>")
    blob.append(content)
    blob.append("<br>")
    blob.append("<hr>")
    blob.append("<i><small>Mackin machine</small></i>")

    return "\n".join(blob)
