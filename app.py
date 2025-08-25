from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

def load_data():
    matches = pd.read_excel("data/liga.xlsx", sheet_name="Matches")
    scorers = pd.read_excel("data/liga.xlsx", sheet_name="Scorers")
    teams = pd.read_excel("data/liga.xlsx", sheet_name="Teams")
    try:
        videos = pd.read_excel("data/liga.xlsx", sheet_name="Videos")
    except:
        videos = pd.DataFrame(columns=["title","embed_url"])

    matches["played"] = matches["home_goals"].notna() & matches["away_goals"].notna()
    results = matches[matches["played"]].copy()
    upcoming = matches[~matches["played"]].copy()

    # tabla general
    standings = []
    for team in teams["team"]:
        played = len(results[(results["home_team"]==team)|(results["away_team"]==team)])
        won = len(results[(results["home_team"]==team)&(results["home_goals"]>results["away_goals"])])
        won += len(results[(results["away_team"]==team)&(results["away_goals"]>results["home_goals"])])
        draw = len(results[(results["home_team"]==team)&(results["home_goals"]==results["away_goals"])])
        draw += len(results[(results["away_team"]==team)&(results["away_goals"]==results["home_goals"])])
        lost = played - won - draw
        goals_for = results.loc[results["home_team"]==team, "home_goals"].sum()
        goals_for += results.loc[results["away_team"]==team, "away_goals"].sum()
        goals_against = results.loc[results["home_team"]==team, "away_goals"].sum()
        goals_against += results.loc[results["away_team"]==team, "home_goals"].sum()
        gd = goals_for - goals_against
        points = won*3 + draw
        standings.append({
            "team": team,
            "played": played,
            "won": won,
            "draw": draw,
            "lost": lost,
            "gf": goals_for,
            "ga": goals_against,
            "gd": gd,
            "points": points
        })
    standings = pd.DataFrame(standings).sort_values(by=["points","gd","gf"], ascending=False).reset_index(drop=True)

    return (results.to_dict(orient="records"),
            upcoming.to_dict(orient="records"),
            standings.to_dict(orient="records"),
            scorers.to_dict(orient="records"),
            videos.to_dict(orient="records"))

@app.route("/")
def index():
    results, upcoming, standings, scorers, videos = load_data()
    return render_template("index.html",
                           results=results[:10],
                           upcoming=upcoming[:10],
                           standings=standings,
                           top_scorers=scorers[:15],
                           videos=videos[:6])

if __name__ == "__main__":
    app.run(debug=True)
