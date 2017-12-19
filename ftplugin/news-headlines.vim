if has('python')
    command! -nargs=1 Python python <args>
elseif has('python3')
    command! -nargs=1 Python python3 <args>
else
    echo "News.vim ERROR: Requires Vim compiled with +python or +python3"
    finish
endif

" Import Python code
execute "Python import sys"
execute "Python sys.path.append(r'" . expand("<sfile>:p:h") . "')"

Python << EOF
if 'news_headlines' not in sys.modules:
    import news_headlines
else:
    import imp
    # Reload python module to avoid errors when updating plugin
    news_headlines = imp.reload(news_headlines)
EOF

" Load front page
execute "Python news_headlines.main()"

noremap <buffer> O :Python news_headlines.open_link()<cr>
noremap <buffer> F :Python news_headlines.fold()<cr>
noremap <buffer> S :Python news_headlines.show_sources()<cr>
noremap <buffer> <CR> :Python news_headlines.go_to_source()<cr>
