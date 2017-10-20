# scrap-custom-trading-watchlist
A simple scraping tool that gathers finance data from different sources on-line visualising them altogether in one watchlist.

scrapit.py reads a list of financial intruments and adresses from macrowatchlist.csv (or similar) and writes a database

guiit.py reads a list (guilist.csv) of organised instruemnts and displays those instruments in a GUI based on that list

guiit.py while bulding the GUI calculates different values and averages from teh database, to calculate those guiit.py uses datait.py where all those operations for values are calculated for each insstrument given from guilist.py 
