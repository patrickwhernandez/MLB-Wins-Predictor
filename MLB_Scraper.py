from bs4 import BeautifulSoup, Comment
import requests
import pandas as pd

years = list(range(2012,2023))
links = ["", "-advanced-batting", "-advanced-pitching"]
dfs_stats = []

def get_url(mlb_season, advanced):
    url = f"https://www.baseball-reference.com/leagues/majors/{mlb_season}{advanced}.shtml"
    return url

def get_soup(url):
    webpage = requests.get(url).text
    soup = BeautifulSoup(webpage, "html.parser")
    comments = BeautifulSoup("".join(soup.find_all(text=lambda text:isinstance(text, Comment))), 'html.parser')
    return soup, comments

def create_dataframes(mlb_season, advanced, soup, comments):
    url = get_url(mlb_season, advanced)
    if "advanced" not in url:
        table = soup.find("table", {"id": "teams_standard_batting"})
        table_rows = table.find_all("tr")
        header = [h.text.strip() for h in table_rows[0].find_all("th")]
        data = [[d.text.strip() for d in table_rows[row].find_all(["th", "td"])]
                for row in range(len(table_rows) - 3) if row != 0]
        df_bat = pd.DataFrame(data, columns=header)
        df_bat.insert(loc=0, column="Year", value=mlb_season)
        
        table_comments = comments.find("table", {"id": "teams_standard_pitching"})
        table_rows_comments = table_comments.find_all("tr")
        header_comments = [h.text.strip() for h in table_rows_comments[0].find_all("th")]
        data_comments = [[d.text.strip() for d in table_rows_comments[row].find_all(["th", "td"])]
                for row in range(len(table_rows_comments) - 3) if row != 0]
        df_pitch = pd.DataFrame(data_comments, columns=header_comments)
        dfs_stats.append(pd.concat([df_bat, df_pitch], axis=1))
    
    elif "batting" in url:
        table = soup.find("table", {"id": "teams_advanced_batting"})
        table_rows = table.find_all("tr")

        header = [h.text.strip() for h in table_rows[1].find_all("th")]
        data = [[d.text.strip() for d in table_rows[row].find_all(["th", "td"])]
                for row in range(len(table_rows) - 3) if row >= 2]
        df_adv_bat = pd.DataFrame(data, columns=header)
        dfs_stats.append(df_adv_bat)

    elif "pitching" in url:
        table = soup.find("table", {"id": "teams_advanced_pitching"})
        table_rows = table.find_all("tr")

        header = [h.text.strip() for h in table_rows[1].find_all("th")]
        data = [[d.text.strip() for d in table_rows[row].find_all(["th", "td"])]
                for row in range(len(table_rows) - 3) if row >= 2]
        df_adv_pitch = pd.DataFrame(data, columns=header)
        dfs_stats.append(df_adv_pitch)
        return df_adv_pitch

for year in years:
    for link in links:
        url = get_url(year, link)
        soup, comments = get_soup(url)
        create_dataframes(year, link, soup, comments)

dfs_seasons = [pd.concat(dfs_stats[i:i+3], axis=1) for i in range(0, len(dfs_stats), 3)]

for df in dfs_seasons:
    df.drop(list(df.filter(regex="EV")), axis=1, inplace=True)
    df.drop(list(df.filter(regex="HardH%")), axis=1, inplace=True)

dfs = pd.concat(dfs_seasons).reset_index(drop=True)

dfs.to_csv("mlb_season_stats.csv")
