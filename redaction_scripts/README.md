## Launch textidote

textidote --check fr --dict textidote_dict.txt --replace textidote_repl.txt --output html backup_210628/main.tex > backup_210628/output.html

As a test:
textidote --check fr --dict textidote_dict.txt --replace textidote_repl.txt --clean <(cat <(echo '\begin{document}') backup_210628/main.tex)


## Latex replace . by , in tables
```python
re.sub(r'([ }{](\d)+)\.', '\1,')
```
