# Catan
An implementation of Explorers of Catan with AI computer player

## Definitions

- Board state. All information about the board. This includes what resources each tile is, what number it has, and where each player has pieces on the board.

- Game state. All knowable information about the game at that point in time with respect to an individual player. This includes who owns what on each space on the board, where the robber is, and what cards each player could have. The results of some player interactions are not known to other players, such as robbing a random card from a player or getting a development card. This means for each player, their knowledge of other players cards will be stored as a range of possible values.

- Asset. Anything purchasable by the player from the bank. Roads, settlements, cities, and development cards (both played and non-played) are all the possible assets.

- Structure. Anything placable on the board. These are roads, settlements, and cities.

- Trade. Any change of game state agreed upon between players. This is not limited to being between just two players, and includes position of the robber, purchasing and non-purchasing of assets, placing and non-placing of structures. Trades are mutually exclusive with promises.

- Promises. Any agreement between players that affects future game states. This includes but is not limited to trade embargoes, future robber placements, future card transactions, and alliances.

- Public knowledge. This is information that anyone who has witnessed the whole history of the game from the perspective of any single player could know. This information is gathered from the results of dice rolls, the state of the board, played development cards, and trades.


## Assumptions

- Non-expansion board is used.
- There are always four players.
- All trades are public knowledge.
- All trades only affect the current board state. Promises about future gameplay are not implemented.
- Knowledge not known to other players is only shared to other players via public actions.
- No probabalistic knowledge is encoded in the game state. If another player has lots of wheat for example and gets stolen from, the information that the stolen card was probably wheat would not be used.


## Implementation

The game state needs to be handled in a way that is symmetrical. If the three other players were to be permuted then that input should be treated identically to the AI player. This will hopefully lead to better training of the AI player as it will be thinking about the game state directly and not whether it is player two or player three who owns something, it will just know that another player owns that thing. This means that any function taking in inputs from multiple players needs to have symmetry in its arguments. For example, $f(x, y, z) = x + y + z$ or $g(x, y, z) = xy + yz + zx$.

Care needs to be taken when processing the board state. A particular position on the board is not important, the only relevant information is where it is relative to resources and structures on the board.

### AI Player

The central component of the AI player is a neural network that takes in a game state, evaluates the position, and gives a probability to each player based on how likely they are to win. Decisions are made by enumerating all reasonable possible options, evaluating the game state, and choosing the game state that results in the best chance to win. By implementing the AI like this, more complicated trades can be added without needing to retrain the network as the only input is the game state.

For board state changes corresponding to trades, the corresponding board states of the other player involved are evaluated and only those where both consider themselves to improve are considered. These trades are then ranked by both players, and the trade where the minimum rank between players is maximised is performed.

The definition of a trade is reasonably broad. The game state includes the position of the robber, and as trades are described by resulting game states, trades including movement of the robber can be added to the list of trades. Trades such as "I will give you xyz if you do not build there" can also be implemented as building is also a change in game state. After either of these types of trades had been handled, the list of trades would have to be updated, for example removing all trades that would move the robber again.