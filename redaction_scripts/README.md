## Launch textidote

textidote --check fr --ignore sh:secmag,sh:figmag,sh:figref,sh:tabmag,sh:tabref \
	--remove-macros texttt,foreign --dict textidote_dict.txt \
	--replace textidote_repl.txt --output html thesis/main.tex > thesis/output.html
As a test:

textidote --check fr --ignore sh:secmag,sh:figmag,sh:figref,sh:tabmag,sh:tabref \
	--remove-macros texttt,foreign --dict textidote_dict.txt \
	--replace textidote_repl.txt --clean <(cat <(echo '\begin{document}') test.tex)


## Latex replace . by , in tables
```python
re.sub(r'([ }{](\d)+)\.', '\1,')
```
