" Highlight links
syn region NHLink start="\[http" end="\]"
highlight link NHLink Comment

" Highlight published at
syn region NHPublishedAt start="(\d\d\d\d" end=")"
highlight link NHPublishedAt Comment

" Highlight sources (check SOURCE_EMPHASIS in news_headlines.py)
syn match NHSource /^⁕⁕⁕.*$/
highlight link NHSource Title

" Highlight Article Titles (check TITLE_EMPHASIS in news_headlines.py)
syn region NHTitle start="^> " end="[^(]*"
highlight link NHTitle String

if exists("b:menu_until_l")
  execute 'syn match NHMenu /\%>0l\%<' . b:menu_until_l . 'l.*/'
  highlight link NHMenu Statement
endif

if exists("b:menu_topics_start_l")
  execute 'syn region NHTopicsMenu start="\%' . b:menu_topics_start_l .
    \ 'l\%' . b:menu_topics_start_c . 'c"' .
    \ ' end="\%' . b:menu_until_l . 'l" containedin=NHMenu'
  highlight link NHTopicsMenu Type
endif

syntax match NHIndexConceal /-/ conceal containedin=NHSource,NHTopicsMenu

" CHANGE COLORS (drop this in .vimrc)
"
" function! SetNHColors()
"   hi link NHSource ctermfg=1 ctermbg=8 guifg=#E12672 guibg=#565656
"   hi link NHLink Statement
"   ...
" endfunction
"
" au! BufEnter,ColorScheme *.news-headlines call SetNHColors()
