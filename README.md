# paper-distiller

## So what's all this about then?

I listen to a *lot* of podcasts and audiobooks. I enjoy processing information aurally, and I also like that it allows me to multitask, e.g. I can wash my dishes while learning about [efforts to solve the water crisis in Mexico City](https://99percentinvisible.org/episode/depave-paradise/). 

As an academic, I also spend a lot of my time reading papers. Recently, I started making my computer read papers out loud to me (there's a lot of text-to-audio software out there for this; I find the reader built into Microsoft Office passable and have been using that), in the hopes that this might convert dry academic writing to a dry robot-voiced podcast. I quickly discovered that this is absolutely infuriating. Between the irrelevant information in page headers and footers, footnotes, citations and the like, listening to a paper pdf's raw information in audio form is something akin to podcast purgatory (and evidently an accessibility nightmare for the visually impaired). So, I decided to write a simple program to strip out this information, essentially distilling the paper for better aural consumption.

## Status

My work on this is ongoing. As of May 19, 2020, the pdf distilling program is operational but not elegant. Short-term goals include:
- Handling footnotes (currently they are read as part of the text)
- Handling different journal formats (I've only tested it with a small number of journals. Every journal has a different format, and my code doesn't always catch the header and footer info in other journals. Again, this seems like an accessibility nightmare.)
- Printing output information to a file instead of the console (I'm still deciding what kind of output file to print to, due to unicode encoding issues)
- Adding a simple UI to make it more user-friendly (e.g., a file browser)

## To use

Everything you need to use this program is in the reader.py file and `distill_file` is the driver function. You will need to have Java installed (version 8 and up) in order for the Tika pdf parser to work; make sure Java is added to your PATH variable as well. 

To run it from CMD (windows terminal), call the `distill_file` function with the name of the pdf to be distilled and the name of the article's journal, e.g.:

`python -c "import reader; reader.distill_file('du_bois_off_print.pdf', 'Synthese')"`

The console output can then be copied to the reader software of your choice. Happy listening!
