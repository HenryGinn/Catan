# Catan
An implementation of Explorers of Catan with a neural network computer player.

## Definitions

- Board state. A subset of the game state which is all information about the board. This includes what resources each tile is, what number it has, and where each player has pieces on the board.

- Board layout. A subset of the board state, this is all static information about the board. No player data is included, this is only the resource and number data for each tile.

- Game state. All knowable information about the game at that point in time with respect to an individual player. This includes who owns what on each space on the board, where the robber is, and what cards each player could have. The results of some player interactions are not known to other players, such as robbing a random card from a player or getting a development card. This means for each player, their knowledge of other players cards will be stored as a range of possible values.

- Real estate. Anything belonging to a player that has been placed on the board. These are roads, settlements, and cities

- Asset. Anything purchasable by the player from the bank. Roads, settlements, cities, and development cards (both played and non-played) are all the possible assets.

- Belongings. This is everything owned by a player, including assets and cards.

- Structure. Anything placable on the board. These are roads, settlements, and cities.

- Trade. Any change of game state agreed upon between relevant players and the bank. This is not limited to being between just two players, and includes position of the robber, purchasing and non-purchasing of assets, placing and non-placing of structures. Trades are mutually exclusive with promises. The bank is included in this definition to allow actions such as two players collaborating to block another player, one who donates resources and the other that builds a road or settlement.

- Promises. Any agreement between players that affects future game states. This includes but is not limited to trade embargoes, future robber placements, future card transactions, and alliances.

- Public knowledge. This is information that anyone who has witnessed the whole history of the game from the perspective of any single player could know. This information is gathered from the results of dice rolls, the state of the board, played development cards, and trades.


## Assumptions

- Non-expansion board is used.
- There are always four players.
- All trades are public knowledge.
- All trades only affect the current board state. Promises about future gameplay are not implemented.
- Knowledge not known to other players is only shared to other players via public actions.
- All probabilities are assumed to be time-dependent Markov chains. For example, suppose player B steals a card from player C, but player A does not know which card. In the future it may be possible for player A to determine this but where other probabilities were already been computed weighted on the probabilities known to A at the time. These probabilities are not recomputed based on the updated knowledge.

The definition of a trade is reasonably broad. The state includes the position of the robber, and as trades are described by resulting game states, trades including movement of the robber can be added to the list of trades. Trades such as "I will give you xyz if you do not build there" can also be implemented as building is also a change in state. After either of these types of trades had been handled, the list of trades would have to be updated, for example removing all trades that would move the robber again.

Promises could still be implemented in this framework. A card similar to a development card could be conjured and then traded with another player, and this card acts like a contract. For example a card could represent, "I owe you one sheep", and then the receiver of this contract card would play the card on a later turn to gain a sheep. Every such promise would need to be implemented as its own card however so the scope would have to be limited. IOU cards could potentially be implemented, but this would increase the card type count by 50% alone and make the network harder to train. Promises such as trade embargos are subject to complicated social dynamics between the players and would be almost impossible to implement.

## Implementation

### Game State and Board State

The game state needs to be handled in a way that is symmetrical. If the three other players were to be permuted then that input should be treated identically to the AI player. This will hopefully lead to better training of the AI player as it will be thinking about the game state directly and not whether it is player two or player three who owns something, it will just know that another player owns that thing. This means that any function taking in inputs from multiple players needs to have symmetry in its arguments. For example, $f(x, y, z) = x + y + z$ or $g(x, y, z) = xy + yz + zx$.

Similar care needs to be taken when processing the board state. A particular position on the board is not important, the only relevant information is where it is relative to resources and structures on the board. A varient of polar coordinates is be used for the board where the angle is discretised. This is for three reasons.

- The radius can be defined uniquelly by the shortest length to the centre hexagon. Rings of constant radius are not equal, and so are not needed to be handled symmetrically - the radius to the centre gives useful information to the player.
- The neural network architecture can be made in such a way to respect the symmetry group of the hexagon, i.e. $D_{12}$. In a similar way to how the player data was handled symmetrically, the board state position can be as well by making all functions of board state symmetrical upon permuting the symmetrical board states. This still gives the network information about the relative position of everything on the board and so it can develop a notion of distance.
- It is well adapted to a hexagonal board. The symmetrical and non-symmetrical coordinates have been perfectly decomposed into the azimuthal and radial components respectively.

The particular nodes associated with each vertex/edge/face does not matter as any change in order is simply a permutation of the rows of the weight matrices in the first layer. The board is defined in terms of its vertices. Each edge is defined by two vertices, and each vertex has a list of tiles associated with it. There are five parts to the board state. The first two are independent of players, but the last three will need to have a node for each player. They are as follows:

- The resource type of a hexagon
- The number associated with a hexagon
- Whether a particular player owns a road on an edge
- Whether a particular player owns a settlement on a vertex
- Whether a particular player owns a city on a vertex

### Implementation and the Neural Network

The central component of the AI player is a neural network that takes in a state, evaluates the position, and gives a probability to each player based on how likely they are to win. Decisions are made by enumerating all reasonable possible options, evaluating the state, and choosing the state that results in the best chance to win. By implementing the AI like this, more complicated trades can be added without needing to retrain the network as the only input is the game state.

For board state changes corresponding to trades, the corresponding states of the other player involved are evaluated and only those where both consider themselves to improve are considered. These trades are then ranked by both players, and the trade where the minimum rank between players is maximised is performed. If player B views a trade favourably for them when player A believes it will not be preferable for B, then player A could gain information about what cards player A has. This information is not used.

The state that the neural networks takes as input needs to be defined in a more precise manner. It needs to be structured in a way that respects the player symmetry, board symmetry, player specific knowledge, and communal knowledge. For example from player A's perspective they might know that player B has a settlement on a particular vertex, but it would be unnecessary to also say that player A knows that player C knows that player B has a settlement on that particular vertex.

What a player believes about a player's belongings (including themselves) can be called a player state. This has two parts, being their cards and their assets. The knowledge of their cards is dependent on the observer player, but the knowledge about their real estate is public. These two halfs also correspond exactly to the different symmetries that need to be obeyed, and are called the card state and the board state respectively. They are stored as two different structures to reflect the structure of the neural network. A game state is the collection of all the player states plus the position of the robber.

There are two subclasses of player: A perspective player, and a regular player. A perspective player contains the knowledge of player A about what cards player B has. The card state is a dictionary stored as an attribute of a perspective player. A player's perspective about themselves is also handled by a perspective player. A regular player stores the real estate information corresponding to that player, and also a list of perspective player objects associated with themselves.

The card state for each player involves a probability distribution for each resource and development card. There are 18 of each card so they will store 19 probabilities per player per card - $P(\text{player} X \text{has} n \text{of card} Y)$. This is because a player can steal a card from another player and it will not be known what that card is, and development cards are chosen randomly. The number of cards of each type possibly remaining that is public knowledge is kept track of, but is not an input into the neural network. It is used only to compute probabilities.

The state needs to be stored in a way where the state of many trades can be easily computed from it, and evaluated by the neural network. A numpy array is used for this as the ability to stack them and pass many game states into the neural network at once outweighs the human-readable advantages of a dictionary. The state is not stored in a single array, and instead reflects the structure of the neural network. The settlement, city, and road states of each player, and the card state of each perspective are stored as their own arrays. The card state is encoded as follows with the lower and upper indexes given inclusively:

### Representation of Trades

A trade is given as a dictionary of dictionaries, where the key is the player name and the value is what they gain of lose. The keys of these inside dictionaries are the types of asset being changed. For all players involved in a trade, they will take both dictionaries and convert it to a state. These states will be compared to their actual player state for each player to determine if it is valid. If this is the case then the trade states will be added to their respective player states if executed. For the input of a trade, the cost of real estate will not be entered, and a preprocessing step will be done to the true gains and losses of the trade.

Development cards are executed by performing a trade. As much of these trade states are computed in advance. For example the harvest trades are always static, and all possible pairs of resources in exchange for a harvest card can be found once at the start of the game. Road builder is similar, although needs to be filtered to ensure only valid roads are built. For knight cards the $19 \cdot 4$ possible trades are precomputed, corresponding to the 19 tiles and 4 players, and these are filtered based on who has property on the tiles. Monopoly cards cannot be precomputed at all as they are completely dependent on the decks of the other players. Victory cards cannot be played, the remain statically in the players deck.
