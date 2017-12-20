filetype plugin on

" Load ftplugin when opening .nnn buffer
au! BufRead,BufNewFile *.nnn set filetype=nnn
au! BufRead,BufNewFile *.nnn-sources set buftype=nofile

" Set required defaults
if !exists("g:nnn_sources")
  let g:nnn_sources = "cnn, bbc-news, wired"
endif

if !exists("g:nnn_topics")
  let g:nnn_topics = ""
endif

if !exists("g:nnn_wrap_text")
  let g:nnn_wrap_text = 120
endif

if !exists("g:nnn_show_published_at")
  let g:nnn_show_published_at = 1
endif

if !exists("g:nnn_default_topic_lang")
  let g:nnn_default_topic_lang = ""
endif

if !exists("g:nnn_default_topic_sort")
  let g:nnn_default_topic_sort = "relevancy"
endif

if !exists("g:nnn_limit_topics_at")
  let g:nnn_limit_topics_at = 10
endif

" Set to 0 to make buffer modifiable
" NOTE: messes the folding if content is deleted
if !exists("g:nnn_nomodifiable")
  let g:nnn_nomodifiable = 1
endif

" Set to 1 to disable threading and make things slow
if !exists("g:nnn_disable_threading")
  let g:nnn_disable_threading = 0
endif

if !exists("g:nnn_browser")
  let g:nnn_browser = ""
endif

function! NNN(...)
  if a:0 > 0
    let g:nnn_arg = a:1
  else
    let g:nnn_arg = ""
  endif

  if g:nnn_nomodifiable > 0
    setlocal modifiable
    execute "edit .nnn"
    normal! gg
    setlocal noma
  else
    execute "edit .nnn"
    normal! gg
  endif
endfunction

" NNN or its alias News
command! -nargs=? News call NNN(<f-args>)
command! -nargs=? NNN call NNN(<f-args>)
