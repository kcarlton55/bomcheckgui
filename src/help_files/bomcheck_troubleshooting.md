# Troubleshooting

    1. CSV OK?
    2. CSV to Excel compare?
    3. Using CSV causes program to crash
    4. Multilevel BOMs
    5. SolidWorks BOM not processed
    6. Assembly pn in Syteline, but SolidWorks BOM not processed.
    7. SyteLine BOM not processed
    8. Empty i q d u fields
    9. SW's lengths not converted to FT
    10. Crash... missing columns
    11. Unable to open config.txt
    12. What accuracy should lengths be?

1. **CSV OK?** SyteLine sometimes default's to exporting to a CSV (.csv) format instead of to an Excel (.xlsx) format. Can a CSV file be used? Yes, however the Excel format is more reliable. Use that.

2. **CSV to Excel compare?** Can an Excel BOM (.xlsx) be compared to a CSV (.csv) BOM? Yes

3. **Using CSV causes program to crash.** The program crashed when when I tried using a CSV format. What can I do? As stated esrlier, use the .xlsx format instead. Character encoding in CSV files can differ depending on the program that generated the CSV file... even if the extension is .csv. The character encoding cannot be seen by human eyes by opening up and looking at the CSV file. Bomcheck sometimes can't correctly interpret the various forms of encoding.

4. **Multilevel BOMs.** SolidWorks BOMs are sometimes multilevel (subassemblies within the main assembly), and the BOMs from SyteLine can be also. Can bomcheck handle these? Yes. In fact, a subassembly in a subassembly in a subassembly, and so forth, can exist. Bomcheck handles any level of subassemblies.

    For a multilevel SolidWorks BOM to work, the Item numbers in the BOM must be numbered to indicate the level; e.g. 1, 2, 3, 3.1, 3.2, 3.2.1, 3.2.2, 3.2.2.1, 3.2.2.2, 3.3 and so forth. For a multilevel SyteLine BOM to work, the BOM must have a column titled Level with values in that column looking like 0, 1, 2, 2.1, 2.2, 2.2.1, 2.2.2, etc. These formats are standard for SolidWorks and Syteline.

5. **SolidWorks BOM not processed.** A SolidWorks BOM I submitted wasn't compared to a SyteLine BOM. The only thing that happend is that the BOM was transformed to look like a BOM from SyteLine. What happened? Answer: no SyteLine BOM was found to compare it to the SolidWorks BOM.

6. **Assembly pn in Syteline, but SolidWorks BOM not processed.** I have a particular assembly/subassembly BOM entered into SyteLine but the bomcheck program reports that that it cannot find the BOM. Why? For that particular assembly, the parts of that assembly have not been entered yet into SyteLine.

7. **SyteLine BOM not processed.** A SyteLine BOM was submitted but nothing happened to indicate that the BOM had even been looked at. What happened? Answer: bomcheck ignores all BOMs from SyteLine for which it can't find a SolidWorks BOM to compare it to.

8. **Empty i q d u fields.** The i, q, d, and u values that indicate pass/fail results are shown empty (       ) for a particular part number. Aren't dashes and/or Xs (---- or --X-, etc.) supposed to be shown? Yes, there should be a dashes or Xs in the i, q, d, u fields. These fields being empty indicates that a part number is repeated in the SyteLine BOM. Duplicate part numbers should not be in a SyteLine BOM.

9. **SW's lengths not converted to FT.** A part length in SolidWorks did not convert of feet in order to compare to a length in SyteLine. Why not? In the bom check you'll see that the unit of measure for length from SolidWorks is EA when it should be FT. This means that the length column is not shown on the SolidWorks BOM as it should be.

10. **Crash... missing columns.** Bomcheck crashed complaining of missing columns. What went wrong? Answer: several things could have happened. A SyteLine BOM may have been mistakenly labeled as as SolidWorks BOM (had _sw.xlsx extension). A SolidWorks BOM may have been labeled as a SyteLine BOM (had a _sl.xlsx extension). The column names for a SolidWorks BOM may not be on the second row of the SW Excel sheet (Dekker's SW BOMs has the assembly part number on the the first row). The column names for a SyteLine BOM are not on the first row. In short, the arrangement of the BOM in the Excel sheet is not in it's normal arrangement.

11. **Unable to open config.txt** (bomcheckgui only) The program reports that it cannot open up a file named config.txt. What is that about? Answer: Whenever a user makes a settings change (File > Settings), bomcheckgui remembers those settings for future use by saving those settings in a file named config.txt. In that file is also saved the last accessed folder containing BOMs. That file is located in a user's settings folder. The file is at C:\Users\username\AppData\Local\bomcheck\config.txt. (The bomcheckgui program automatically creates this file.) Perhaps user rights were somehow severed??? Contact the IT manager for help.

13. **What accuracy should lengths be?** At File > Settings the decimal place accuracy is set for rounding bomcheck lengths (e.g. .83 ft). An accuracy of 2 is a good number. This means that if two places are shown, then the length is accurate to within ±0.06 inches. This is close enough. Then if the lengths shown in SolidWorks and SyteLine differ by more than ±0.06 inches, then bomcheck will flag this as an error. Of course, a greater level of accuracy can be set.