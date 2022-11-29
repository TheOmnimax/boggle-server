# Sequence diagrams

A solid line is an action initiated by the player, and a dotted line is an action initiated automatically by the app or the server.

## Game creation

```mermaid
sequenceDiagram
autonumber
  App->>Server: Create game room
  activate Server
  Server-->>App: Game room created: room_code
  deactivate Server
  App-->>Server: Create game: room_code, width, height, time, name
  activate Server
  Server-->>App: Game created: player_id
  deactivate Server
```
Note: When the app is told that the game room has been created, it will automatically then request the game itself being created, without any prompting from the user.

## Join game

```mermaid
sequenceDiagram
autonumber
  App->>Server: Join game: room_code, name
  activate Server
  Server-->>App: Add player to room: player_id
  deactivate Server
```

## Playing game

```mermaid
sequenceDiagram
autonumber
  App->>Server: Game is started by host.
  activate Server
  loop Every second
    App->>Server: Check into server
    Server-->>App: Game info, including if started or ended
  end
  App->>Server: Word entered by player
  activate Server
  Server-->>App: Word status, including if it was accepted
  deactivate Server
  Server-->>App: Game ended
  deactivate Server
```

## Get results

```mermaid
sequenceDiagram
autonumber
  App->>Server: Request game results: room_code
  activate Server
  Server-->>App: Results sent to player: shared_words, player_data,<br>winning_score, winner_names, missed_words
  deactivate Server
```

