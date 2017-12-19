# -*- coding: utf-8 -*-

from __future__ import print_function, division
import os
import json
import sys
import re
import textwrap
import vim
import webbrowser
import collections
import threading
from datetime import datetime
if sys.version_info >= (3, 0):
    from html.parser import HTMLParser
    from urllib.request import urlopen
    from urllib.parse import urlencode
    unicode = bytes
    unichr = chr
else:
    from HTMLParser import HTMLParser
    from urllib2 import urlopen
    from urllib import urlencode


API_KEY = os.getenv('VIM_NEWS_API_KEY')
SOURCE_EMPHASIS = '⁕⁕⁕'
TITLE_EMPHASIS = '> '
SOURCE_FOLDS = collections.OrderedDict()
GROUPS = []  # sources, topics
MENU = []  # menu items


class GetNews:
    def __init__(self, api_key, with_threading=True):
        self.api_key = api_key
        self.with_threading = with_threading
        self.api_base_url = 'https://newsapi.org/v2'
        self.default_topic_lang = None
        self.default_topic_sort = None
        self.limit_topics_at = None

    def _sort_by_date(self, l, time_format='\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'):
        """Try to sort by most recent articles first."""
        k = 'publishedAt'
        if not l:
            return l
        for i in l:
            try:
                d = i[k]
            except KeyError:
                i[k] = ''
                d = i[k]
            if not re.match(time_format, str(d)):
                if d:
                    return l
        sorted_l = sorted(
            l,
            key=lambda x: x[k] if x[k] else '',
            reverse=True
        )
        return sorted_l

    def _cleanup_duplicates(self, l):
        """Sometimes newsapi.org reurns duplicates."""
        if not l: return l
        clean_l = [l[0]]
        for i in l:
            if not i['url'] in (x['url'] for x in clean_l):
                clean_l.append(i)
        return clean_l

    def get_sources(self, filters=None):
        """Get news sources.
        filters: <dict> filter the response

        documentation:
          https://newsapi.org/docs/endpoints/sources
        """
        url = '%s/sources?apiKey=%s' % (self.api_base_url, self.api_key)
        response = json.loads(urlopen(url, timeout=5).read().decode('utf-8'))
        sources = response['sources']
        if filters:
            sources = list(filter(
                lambda x: all(x[y] == z for y, z in filters.items()), sources))
        return sources

    def get_top_headlines(self, sources):
        """Get top headlines.
        sources: <str> 'bbc-news, cnn, ...'

        documentation:
          https://newsapi.org/docs/endpoints/top-headlines
        """
        url = '%s/top-headlines?apiKey=%s&sources=%s' % (self.api_base_url,
                                                         self.api_key, sources)
        response = json.loads(urlopen(url, timeout=5).read().decode('utf-8'))
        return response['articles']

    def get_by_topic(self, topic, language=None, sort_by=None):
        """Get headlines by topic."""
        now = datetime.utcnow()
        _from = ('%s-%s-%s' % (now.year, now.month, now.day - 1))
        params = {'apiKey': self.api_key, 'q': topic, 'from': _from}
        if language:
            params['language'] = language
        elif self.default_topic_lang:
            params['language'] = self.default_topic_lang
        if sort_by:
            params['sortBy'] = sort_by
        elif self.default_topic_sort:
            params['sortBy'] = self.default_topic_sort
        url = '%s/everything?%s' % (self.api_base_url, urlencode(params))
        response = json.loads(urlopen(url, timeout=5).read().decode('utf-8'))
        return response['articles']

    def group_by_source(self, sources, sorted_by_date=True, limit_at=False):
        """Parse headlines and group them by source
        sources: <str> 'bbc-news, cnn, ...'
        limit_at: remove items until this number of items remain
        return: <dict>
        """
        sources = sources.replace(' ', '')  # the news sources have no spaces
        headlines = self.get_top_headlines(sources)
        grouped_by_source = collections.OrderedDict()

        for s in sources.split(','):
            grouped_by_source[s] = []
        for headline in headlines:
            if headline['title'] and headline['url']:
                source = headline['source']['id']
                if source in grouped_by_source.keys():
                    grouped_by_source[source].append(headline)
        if sorted_by_date:
            for k, v in grouped_by_source.items():
                grouped_by_source[k] = self._sort_by_date(v)
        if limit_at:
            for k, v in grouped_by_source.items():
                if v: grouped_by_source[k] = v[:limit_at]
        return grouped_by_source

    def group_by_topic(self, topics, sorted_by_date=True):
        """Parse headlines and group them by topic
        topics: <list> [{'topic': 'apple', 'language': 'en'}, {'topic': ...}]
        return: <dict>
        """
        grouped_by_topic = collections.OrderedDict()

        def dict_updater(topic, headlines):
            for headline in headlines:
                if headline['title'] and headline['url']:
                    if topic in grouped_by_topic.keys():
                        grouped_by_topic[topic].append(headline)
                    else:
                        grouped_by_topic[topic] = []

        def send_request(topic):
            if ('sort_by' in topic.keys()) and topic['sort_by']:
                _sort_by = topic['sort_by']
            else:
                _sort_by = None
            if ('language' in topic.keys()) and topic['language']:
                topic_name = '%s(%s)' % (topic['topic'].replace(' ', '-'), topic['language'])
                headlines = self.get_by_topic(
                    topic['topic'],
                    language=topic['language'],
                    sort_by=_sort_by
                )
                dict_updater(topic_name, headlines)
            else:
                headlines = self.get_by_topic(topic['topic'], sort_by=_sort_by)
                dict_updater(topic['topic'].replace(' ', '-'), headlines)

        if self.with_threading:
            threads = []
            for topic in topics:
                t = threading.Thread(target=send_request, args=[topic])
                t.daemon = True
                t.start()
                threads.append(t)

            for t in threads:
                t.join()
        else:
            for topic in topics:
                send_request(topic)

        if sorted_by_date:
            for k, v in grouped_by_topic.items():
                grouped_by_topic[k] = self._sort_by_date(v)
        if self.limit_topics_at:
            for k, v in grouped_by_topic.items():
                if v: grouped_by_topic[k] = v[:self.limit_topics_at]
        for k, v in grouped_by_topic.items():
            grouped_by_topic[k] = self._cleanup_duplicates(v)
        return grouped_by_topic


def write_to_buff(s):
    """Write string to current buffer."""
    current_buff = vim.current.buffer

    # buffer.append() cannot accept unicode type,
    # must first encode to UTF-8 string
    if isinstance(s, unicode):
        s = s.encode('utf-8', errors='replace')
    else:
        current_buff.append(s)


def set_folds():
    """Save into SOURCE_FOLDS the line numbers where folds can be created."""
    for ln_nr, ln in enumerate(vim.current.buffer):
        if ln.startswith(SOURCE_EMPHASIS):
            source = ln.strip().strip(SOURCE_EMPHASIS).strip()
            SOURCE_FOLDS[source] = ln_nr + 1
    SOURCE_FOLDS['<EOF>'] = int(vim.eval('line("$")'))


def buffer_setup():
    settings = (
        'noswapfile', 'buftype=nofile',
        'nonumber', 'cc=', 'conceallevel=1',
        'concealcursor=n'
    )
    for setting in settings:
        vim.command('setlocal ' + setting)
    for token in ('(', ')', '-', '$'):
        vim.command('setlocal isk+=%s' % token)


def first_group_ends_at(menu, title):
    for l, c in enumerate(menu):
        found = c.lower().find(title.lower())
        if found != -1:
            loc = (l + 1, found + len(title) + 1)
            return loc

def set_buffer_vars(sources, groups, menu):
    """Set vars used for syntax highlighting."""
    t_start_l = 1
    t_start_c = 1

    if sources:
        s_end = first_group_ends_at(menu, list(groups[0].keys())[-1])
        if s_end:
            t_start_l = s_end[0]
            t_start_c = s_end[1] + 1
    vim.command('let b:menu_topics_start_l=%s' % t_start_l)
    vim.command('let b:menu_topics_start_c=%s' % t_start_c)
    vim.command('let b:menu_until_l=%s' % (len(menu) + 1))


def open_link():
    """Open link in default browser."""
    def get_url(line_nr):
        line_number = line_nr - 1
        line = vim.current.buffer[line_number]
        if not line:
            return
        if line.startswith('[http'):
            inc = 1
            while True:
                if line[-1] == ']':
                    return line[1:-1]
                line += vim.current.buffer[line_number + inc]
                inc += 1
        return get_url(line_nr + 1)

    current_line_nr, _ = vim.current.window.cursor
    url = get_url(current_line_nr)

    if url:
        browser = webbrowser.get()
        browser.open(url)


def fold():
    def try_range(folds, line_nr):
        start, end = folds[0], folds[1] - 1
        if len(folds) == 2:
            return start, end
        if folds[0] <= line_nr <= folds[1]:
            return start, end
        return try_range(folds[1:], line_nr)

    current_line_nr, _ = vim.current.window.cursor
    start, stop = try_range(list(SOURCE_FOLDS.values()), current_line_nr + 1)

    if int(vim.eval('foldlevel(%s)' % (current_line_nr + 1))) > 0:
        try:
            vim.command('normal za')
        except vim.error as e:
            print('WARNING: %s' % e)
    else:
        try:
            vim.command('%s,%sfold' % (start, stop))
        except vim.error as e:
            print('WARNING: %s' % e)


def show_sources():
    """Print all possible news sources."""
    news = GetNews(API_KEY)
    sources = map(lambda x: str(x['id']), news.get_sources())
    vim.command('new .news-headlines-sources')
    for i in sources:
        write_to_buff(i)
    del vim.current.buffer[0]


def go_to_source():
    word_under_cursor = vim.eval('expand("<cWORD>")')
    if word_under_cursor in SOURCE_FOLDS.keys():
        target_line = str(SOURCE_FOLDS[word_under_cursor])
        vim.command(target_line)
        vim.command('normal zt')


def parse_vim_args(g_arg):
    """Turn g:news_headlines_args into sources and topics.

    the pattern is:
        sources:
          > are one word or words separated by -
          > they must match the newsapi sources
          > eg: bbc-news
        topics:
          > start with / and can be multiple words
          > use : to specify first language and then sort_by
          > eg: /bitcoin:en:popularity

    topics and sources can be be chained with commas

    eg: cnn, bbc-news, /bitcoin::popularity
    """
    sources = ''
    topics = []
    t_keys = ['topic', 'language', 'sort_by']

    args = (arg.strip() for arg in g_arg.split(','))

    for arg in args:
        if arg.startswith('/'):
            t_dict = dict(zip(t_keys, arg.lstrip('/').strip().split(':')))
            topics.append(t_dict)
        elif sources:
            sources += ',%s' % arg
        else:
            sources += arg
    return {'sources': sources, 'topics': topics}


def main():
    buffer_setup()

    # user customizable vars
    wrap_text = int(vim.eval('g:news_headlines_wrap_text'))
    show_published_at = int(vim.eval('g:news_headlines_show_published_at'))
    default_topic_lang = vim.eval('g:news_headlines_default_topic_lang')
    default_topic_sort = vim.eval('g:news_headlines_default_topic_sort')
    limit_topics_at = int(vim.eval('g:news_headlines_limit_topics_at'))
    disable_threading = int(vim.eval('g:news_headlines_disable_threading'))
    cmd_line_args = vim.eval('g:news_headlines_arg')

    if cmd_line_args:
        args = parse_vim_args(cmd_line_args)
        sources = args['sources']
        topics = args['topics']
    else:
        sources = vim.eval('g:news_headlines_sources')
        topics = vim.eval('g:news_headlines_topics')

    if not sources and not topics:
        print('No sources or topics selected. Check the help (:help news-headlines)')
        return

    html = HTMLParser()

    news = GetNews(API_KEY, with_threading=True)
    news.default_topic_lang = default_topic_lang
    news.default_topic_sort = default_topic_sort
    news.limit_topics_at = limit_topics_at
    if disable_threading:
        news.with_threading = False

    if sources: GROUPS.append(news.group_by_source(sources))
    if topics: GROUPS.append(news.group_by_topic(topics))

    wrapper = textwrap.TextWrapper(width=wrap_text)
    menu_wrapper = textwrap.TextWrapper(
        width=wrap_text, break_on_hyphens=False,
        break_long_words=False
    )
    title_wrapper = textwrap.TextWrapper(
        width=wrap_text, initial_indent=TITLE_EMPHASIS,
        subsequent_indent=TITLE_EMPHASIS
    )

    def _write_content(groups):
        for group in groups:
            for title, headlines in group.items():
                write_to_buff('%s %s %s' % (SOURCE_EMPHASIS, title.upper(), SOURCE_EMPHASIS))
                write_to_buff('')
                if not headlines:
                    continue
                for h in headlines:
                    if show_published_at and h['publishedAt']:
                        published_at = ' (%s)' % h['publishedAt']
                    else:
                        published_at = ''
                    write_to_buff(title_wrapper.wrap(html.unescape(h['title'] + published_at)))
                    if h['description']:
                        write_to_buff(
                            wrapper.wrap(html.unescape(h['description'].lstrip(TITLE_EMPHASIS)))
                        )
                    write_to_buff(wrapper.wrap('[' + html.unescape(h['url'] + ']')))
                    write_to_buff('')

    def _write_menu(groups, menu):
        to_write = []
        for group in groups:
            to_write.append('   '.join(map(lambda x: x.upper(), group.keys())))
        menu.extend(menu_wrapper.wrap('   '.join(to_write)))
        write_to_buff(menu)
        write_to_buff('')

    _write_menu(GROUPS, MENU)
    if not MENU:
        print('No articles found. Try to refine your search.')
        return
    _write_content(GROUPS)
    set_buffer_vars(sources, GROUPS, MENU)

    del vim.current.buffer[0]
    set_folds()
