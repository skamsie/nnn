if has('python')
    command! -nargs=1 Python python <args>
elseif has('python3')
    command! -nargs=1 Python python3 <args>
else
    echo "nnn.vim ERROR: Requires Vim compiled with +python or +python3"
    finish
endif

" Import Python code
execute "Python import sys"
execute "Python sys.path.append(r'" . expand("<sfile>:p:h") . "')"

Python << EOF
if 'nnn' not in sys.modules:
    import nnn
else:
    import imp
    # Reload python module to avoid errors when updating plugin
    nnn = imp.reload(nnn)
EOF

" Load front page
execute "Python nnn.main()"

noremap <buffer> O :Python nnn.open_link()<cr>
noremap <buffer> F :Python nnn.fold()<cr>
noremap <buffer> S :Python nnn.show_sources()<cr>
noremap <buffer> <CR> :Python nnn.go_to_source()<cr>
