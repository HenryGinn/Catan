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

### Game State and Board State

The game state needs to be handled in a way that is symmetrical. If the three other players were to be permuted then that input should be treated identically to the AI player. This will hopefully lead to better training of the AI player as it will be thinking about the game state directly and not whether it is player two or player three who owns something, it will just know that another player owns that thing. This means that any function taking in inputs from multiple players needs to have symmetry in its arguments. For example, $f(x, y, z) = x + y + z$ or $g(x, y, z) = xy + yz + zx$.

Similar care needs to be taken when processing the board state. A particular position on the board is not important, the only relevant information is where it is relative to resources and structures on the board. A varient of polar coordinates is be used for the board where the angle is discretised. This is for three reasons.

- The radius can be defined uniquelly by the shortest length to the centre hexagon. Rings of constant radius are not equal, and so are not needed to be handled symmetrically - the radius to the centre gives useful information to the player.
- The neural network architecture can be made in such a way to respect the symmetry group of the hexagon, i.e. $D_{12}$. In a similar way to how the player data was handled symmetrically, the board state position can be as well by making all functions of board state symmetrical upon permuting the symmetrical board states. This still gives the network information about the relative position of everything on the board and so it can develop a notion of distance.
- It is well adapted to a hexagonal board. The symmetrical and non-symmetrical coordinates have been perfectly decomposed into the azimuthal and radial components respectively.

The particular nodes associated with each vertex/edge/face does not matter as any change in order is simply a permutation of the rows of the weight matrices in the first layer. The board is defined in terms of its vertices. Each edge is defined by two vertices, and each vertex has a list of hexagons associated with it. There are five parts to the board state. The first two are independent of players, but the last three will need to have a node for each player. They are as follows:

- The resource type of a hexagon
- The number associated with a hexagon
- Whether a particular player owns a road on an edge
- Whether a particular player owns a settlement on a vertex
- Whether a particular player owns a city on a vertex

### AI Player

The central component of the AI player is a neural network that takes in a game state, evaluates the position, and gives a probability to each player based on how likely they are to win. Decisions are made by enumerating all reasonable possible options, evaluating the game state, and choosing the game state that results in the best chance to win. By implementing the AI like this, more complicated trades can be added without needing to retrain the network as the only input is the game state.

For board state changes corresponding to trades, the corresponding board states of the other player involved are evaluated and only those where both consider themselves to improve are considered. These trades are then ranked by both players, and the trade where the minimum rank between players is maximised is performed.

The definition of a trade is reasonably broad. The game state includes the position of the robber, and as trades are described by resulting game states, trades including movement of the robber can be added to the list of trades. Trades such as "I will give you xyz if you do not build there" can also be implemented as building is also a change in game state. After either of these types of trades had been handled, the list of trades would have to be updated, for example removing all trades that would move the robber again.