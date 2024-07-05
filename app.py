import random
import pandas as pd
import streamlit as st

class Player:
    def __init__(self, name, team):
        self.name = name
        self.team = team
        self.goal_difference = 0
        self.matches = 0
        self.points = 0
        self.wins = 0
        self.losses = 0
        self.draws = 0

    def __str__(self):
        return f"{self.name} ({self.team})"

def create_players(num_players):
    players = []
    for i in range(num_players):
        name = st.text_input(f'Qual nome do jogador {i + 1}?', key=f'name_{i}')
        team = st.text_input(f'Qual time do {name}?', key=f'team_{i}')
        name = name.title()
        team = team.title()
        players.append(Player(name, team))
    return players

def generate_matches(players):
    matches = []
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            matches.append((players[i], players[j]))
    random.shuffle(matches)
    return matches

def update_table(table, match, score1, score2):
    player1, player2 = match
    goal_diff = score1 - score2
    player1.goal_difference += goal_diff
    player2.goal_difference -= goal_diff
    player1.matches += 1
    player2.matches += 1
    if score1 > score2:
        player1.wins += 1
        player1.points += 3
        player2.losses += 1
    elif score1 < score2:
        player2.wins += 1
        player2.points += 3
        player1.losses += 1
    else:
        player1.draws += 1
        player2.draws += 1
        player1.points += 1
        player2.points += 1

    update_dataframe(table, player1)
    update_dataframe(table, player2)

def undo_update_table(table, match, score1, score2):
    player1, player2 = match
    goal_diff = score1 - score2
    player1.goal_difference -= goal_diff
    player2.goal_difference += goal_diff
    player1.matches -= 1
    player2.matches -= 1
    if score1 > score2:
        player1.wins -= 1
        player1.points -= 3
        player2.losses -= 1
    elif score1 < score2:
        player2.wins -= 1
        player2.points -= 3
        player1.losses -= 1
    else:
        player1.draws -= 1
        player2.draws -= 1
        player1.points -= 1
        player2.points -= 1

    update_dataframe(table, player1)
    update_dataframe(table, player2)

def update_dataframe(df, player):
    df.loc[df['Jogador'] == str(player), ['P', 'SG', 'V', 'E', 'D', 'Pts']] = [
        player.matches, player.goal_difference, player.wins, player.draws, player.losses, player.points]

def display_table(df):
    if 'Pts' in df.columns:
        st.dataframe(df.sort_values(by='Pts', ascending=False))
    else:
        st.dataframe(df)
        st.write("Debug: Columns in the DataFrame are: ", df.columns.tolist())

def display_next_matches(matches, num=3):
    st.header("Próximas Partidas")
    for i in range(min(num, len(matches))):
        st.write(f"Partida {i + 1}: {matches[i][0]} vs {matches[i][1]}")

def parse_score_input(score_input):
    if 'x' in score_input:
        return map(int, score_input.split('x'))
    elif ' ' in score_input:
        return map(int, score_input.split())
    else:
        raise ValueError("Formato Invalido. Use '2x1' ou '2 1'.")

def reset_league():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# Streamlit App
def main():
    st.title("Copa Cirrose")

    num_players = st.number_input('Qual numero de jogadores?', min_value=2, step=1, key='num_players')

    if 'players' not in st.session_state or len(st.session_state.players) != num_players:
        st.session_state.players = [Player("", "") for _ in range(num_players)]

    for i in range(num_players):
        st.session_state.players[i].name = st.text_input(f'Qual nome do jogador {i + 1}?',
                                                         value=st.session_state.players[i].name, key=f'name_{i}')
        st.session_state.players[i].team = st.text_input(f'Qual time do {st.session_state.players[i].name}?',
                                                         value=st.session_state.players[i].team, key=f'team_{i}')

    if st.button("Gerar Partidas"):
        st.session_state.matches = generate_matches(st.session_state.players)
        st.session_state.table = pd.DataFrame({
            'Jogador': [str(player) for player in st.session_state.players],
            'P': [0] * num_players,
            'SG': [0] * num_players,
            'V': [0] * num_players,
            'E': [0] * num_players,
            'D': [0] * num_players,
            'Pts': [0] * num_players,
        })
        st.session_state.match_history = []

    if 'matches' in st.session_state and 'table' in st.session_state:
        display_table(st.session_state.table)

        if st.session_state.matches:
            display_next_matches(st.session_state.matches)

            match = st.session_state.matches[0]
            st.subheader(f"Partida Atual: {match[0]} vs {match[1]}")
            score_input = st.text_input("Qual foi o placar? (ex: 2x1 ou 2 1)", key='score_input')

            if st.button("Atualizar Jogo"):
                if score_input:
                    try:
                        score1, score2 = parse_score_input(score_input)
                        st.session_state.match_history.append((match, score1, score2))
                        st.session_state.matches.pop(0)
                        update_table(st.session_state.table, match, score1, score2)
                        st.success("Pontos atualizados")
                    except ValueError as e:
                        st.error(e)
                st.rerun()

            if st.button("Desfazer Última Partida"):
                if st.session_state.match_history:
                    last_match, last_score1, last_score2 = st.session_state.match_history.pop()
                    undo_update_table(st.session_state.table, last_match, last_score1, last_score2)
                    st.session_state.matches.insert(0, last_match)
                    st.success("Última partida desfeita")
                else:
                    st.error("Nenhuma partida para desfazer")
                st.rerun()
        else:
            st.write("Todas as partidas jogadas. Começou o mata-mata.")

    if st.button("Reiniciar Liga"):
        reset_league()

if __name__ == "__main__":
    main()