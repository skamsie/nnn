# nnn

News in Vim. ⁽(◍˃̵͈̑ᴗ˂̵͈̑)⁽  
This is pretty much a vim / neovim interface for https://newsapi.org  


![Alt text](https://github.com/skamsie/nnn/raw/master/nnn.png)

### Setup

Requirements

* Neovim or Vim compiled with python3 support  
* An api key for newsapi.org (https://newsapi.org/register). It is free for non
  commercial use
* Add the following line to your .bashrc or .zshrc and reload the terminal  
  `export VIM_NEWS_API_KEY=<your_api_key>`


Install with your favorite plugin manager  
`Plug 'skamsie/nnn'`

### Usage

The main command `:NNN` is used to load the news content in a new buffer.

<strong>Without any arguments</strong>

It uses the configuration to look for articles. `:help nnn-configuration`

**With arguments**

You can pass sources and topics as arguments, and the results will be returned
based on them instead of the variables configured in your .vimrc. You can pass
both sources and topics separated by commas.

Sources are the source ids from newsapi.org. Use `S` to show all sources or
check the api documentation.

Topics have to start with a `/` and consist of a string of one word or more words
separated by whitespace. The language of the results as well as the desired
sorting algorithm can be specified by using `:` and the language abbreviation,
followed by `:` and the sorting type. They are however optional and if not
specified the defaults will be used (see `:help nnn-configuration` for defaults)

**Examples**

```vim
"Search for articles from cnn only
:NNN cnn

"Search for multiple topics
:NNN /vim, /bitcoin:en:popularity, /climate change::relevancy

"Search sources and topics:
:NNN bbc-news, /bitcoin:en:popularity
```

**Buffer commands**

* `O` Open the article in browser (while cursor is on title or description)
* `F` Folds or unflods the articles under the current source
* `S` Show all possible news sources
* `<CR>` While on the top index bar, goes to the corresponding section

Everything else is in the [documentation](https://github.com/skamsie/nnn/raw/master/doc/nnn.txt)

`:help nnn`

