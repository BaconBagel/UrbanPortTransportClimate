import pandas as pd

# Read the CSV file
df = pd.read_csv("unweighted-rivers - weighted_River_flood_extent_2071_2100_RCP85_with_protection.csv")

# Open a text file for writing with UTF-8 encoding
with open("output_2_DiD.txt", "w", encoding="utf-8") as f:
    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        # Extract GM_NAAM and Displacement Index from the row
        GM_NAAM = row['Municipality_Name']
        Displacement_Index = row['DiD']

        # Generate the line with the replacements
        #line = f'replace Hs={Displacement_Index} if origin=="{GM_NAAM}"\n'
        line = f'replace Omegacf=Omega*({Displacement_Index}^($beta/(1+$alpha*$beta))) if origin=="{GM_NAAM}"\n'

        # Write the line to the text file
        f.write(line)
