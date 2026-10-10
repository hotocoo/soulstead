# Online Play — Friends on Different Networks

**Requirement:** friends join with a lobby code from anywhere on the internet. No LAN, no
"same WiFi", no port forwarding on any player's router.

## How it works

```
 Player A (home WiFi)  ─┐
 Player B (mobile data) ─┼──► outbound WSS ──►  relay server (public host)
 Player C (other city) ─┘                        owns lobby codes
                                                 forwards Chronicle entries
```

Every player, including whoever created the lobby, is a **client** that connects *outbound*
to a public relay. Outbound connections traverse NAT and consumer routers without
configuration, which is why no player needs to open a port. Only the relay needs a public
address, and it is a single small process.

The relay is deliberately thin:

- It owns lobby codes and membership (max 4 players per lobby).
- It forwards **Chronicle entries** (consequence) reliably and **body state** unreliably.
- It keeps a short ledger copy so a late joiner starts from the same ending-drift.
- It stores no accounts and drops a lobby 120 seconds after the last player leaves.

## Client side

`game/src/net/net_session.gd`:

```gdscript
NetSession.create_lobby("Ashfall Hold")            # returns a code via lobby_joined
NetSession.join_lobby("K7QM2P", "Verren Hold")     # friend types the code
NetSession.join_direct("192.168.1.20")             # LAN / self-hosted fallback
```

Relay URL resolution order:

1. `SOULSTEAD_RELAY` environment variable (per-machine override, handy for testing).
2. The `url` argument passed to `create_lobby` / `join_lobby`.
3. `DEFAULT_RELAY_URL` (`wss://relay.soulstead.game`).

## Running the relay

### Local test (two machines, or two instances on one machine)

```bash
godot --headless --path server
# then launch the game with:
SOULSTEAD_RELAY=ws://127.0.0.1:8080 godot --path game
```

### Docker

```bash
docker build -t soulstead-relay server/
docker run -e PORT=8080 -p 8080:8080 soulstead-relay
```

### fly.io (recommended for a friends group)

```bash
cd server
fly launch --no-deploy      # once; keeps the provided fly.toml
fly deploy
```

Then point the client at it:

```
SOULSTEAD_RELAY=wss://soulstead-relay.fly.dev
```

`force_https = true` in `fly.toml` means the client must use `wss://`, which also keeps the
traffic encrypted. `auto_stop_machines = "suspend"` keeps the idle cost near zero for a
private group; the first connection wakes it.

### No server at all: a tunnel

For a one-evening session, run the relay on one player's machine and expose it with a tunnel
(any of `cloudflared`, `ngrok`, `playit.gg`):

```bash
godot --headless --path server &
cloudflared tunnel --url http://localhost:8080
# share the wss:// URL it prints; everyone sets SOULSTEAD_RELAY to it
```

This still avoids router configuration: the tunnel client also connects outbound.

## What multiplayer changes about the game

Co-op is not a damage-sharing mode. It is a **shared consequence** mode:

| Co-op action | Ledger effect | Felt by |
|---|---|---|
| Reclaim an ally's Echo | `echo_reclaimed` | Both settlements' Memory and Mercy rise |
| Leave a downed ally | `ally_abandoned` | Communion collapses for everyone in the lobby |
| Lift a downed ally | `ally_revived` | Communion and Mercy rise for everyone |
| Bury a stranger's drifted Echo | `foreign_echo_honoured` | Pushes the lobby toward **The Open Hearth** |
| Kill a stranger's drifted Echo | `foreign_echo_slain` | Pushes toward **The Long Hold** |

Because endings resolve from the shared ledger, a friend who plays cruelly in your lobby
moves your ending too. That is the intended stake: in a Successor-Sim the other player is
another lineage whose choices your settlement has to live with.

## Asynchronous play (no lobby needed)

`game/src/net/echo_exchange.gd` writes a roaming Echo to `user://drift/outbox` as a small
JSON file. Dropping that file into another player's `user://drift/inbox` spawns it in their
world, carrying its original owner's name and build. How they resolve it — kill it or bury it
— writes back into *their* Chronicle. The relay can carry these too; the file format is the
message either way.
