filetype plugin on

" Load ftplugin when opening .news-headlines buffer
au! BufRead,BufNewFile *.news-headlines set filetype=news-headlines
au! BufRead,BufNewFile *.news-headlines-sources set buftype=nofile

" Set required defaults
if !exists("g:news_headlines_sources")
  let g:news_headlines_sources = "cnn, bbc-news, wired"
endif

if !exists("g:news_headlines_topics")
  let g:news_headlines_topics = ""
endif

if !exists("g:news_headlines_wrap_text")
  let g:news_headlines_wrap_text = 120
endif

if !exists("g:news_headlines_show_published_at")
  let g:news_headlines_show_published_at = 1
endif

if !exists("g:news_headlines_default_topic_lang")
  let g:news_headlines_default_topic_lang = ""
endif

if !exists("g:news_headlines_default_topic_sort")
  let g:news_headlines_default_topic_sort = "relevancy"
endif

if !exists("g:news_headlines_limit_topics_at")
  let g:news_headlines_limit_topics_at = 10
endif

" Set to 0 to make buffer modifiable
" NOTE: messes the folding if content is deleted
if !exists("g:news_headlines_nomodifiable")
  let g:news_headlines_nomodifiable = 1
endif

" Set to 1 to disable threading and make things slow
if !exists("g:news_headlines_disable_threading")
  let g:news_headlines_disable_threading = 0
endif

function! NewsHeadlines(...)
  if a:0 > 0
    let g:news_headlines_arg = a:1
  else
    let g:news_headlines_arg = ""
  endif

  if g:news_headlines_nomodifiable > 0
    setlocal modifiable
    execute "edit .news-headlines"
    normal! gg
    setlocal noma
  else
    execute "edit .news-headlines"
    normal! gg
  endif
endfunction

command! -nargs=? News call NewsHeadlines(<f-args>)
