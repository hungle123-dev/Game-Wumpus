import os
from Source.Game import Game
from Source.Entity.Board import Board
from Source.Run.HybridAgent import HybridAgent
from Source.Run.RandomAgentSimple import RandomAgentSimple

def run_comparison():
	config = {
		'grid_size': 8,
		'num_wumpus': 2,
		'pit_density': 0.2,
		'num_tests': 30,
		'mode': 'random'
	}
	smart_results = []
	random_results = []
	for test_num in range(1, config['num_tests'] + 1):
		# Smart Agent
		game = Game(grid_size=config['grid_size'], num_wumpus=config['num_wumpus'], pit_density=config['pit_density'])
		board = Board(config['grid_size'], config['grid_size'])
		agent = HybridAgent()
		result = game.run(agent)
		smart_results.append({
			'test': test_num,
			'won': result['win'],
			'score': result['score'],
			'moves': result['moves']
		})
		# Random Agent
		game = Game(grid_size=config['grid_size'], num_wumpus=config['num_wumpus'], pit_density=config['pit_density'])
		board = Board(config['grid_size'], config['grid_size'])
		agent = RandomAgentSimple()
		result = game.run(agent)
		random_results.append({
			'test': test_num,
			'won': result['win'],
			'score': result['score'],
			'moves': result['moves']
		})
	# Statistics
	smart_wins = sum(1 for r in smart_results if r['won'])
	smart_avg_score = sum(r['score'] for r in smart_results) / config['num_tests']
	smart_avg_moves = sum(r['moves'] for r in smart_results) / config['num_tests']
	random_wins = sum(1 for r in random_results if r['won'])
	random_avg_score = sum(r['score'] for r in random_results) / config['num_tests']
	random_avg_moves = sum(r['moves'] for r in random_results) / config['num_tests']
	# Output
	lines = []
	lines.append("WUMPUS WORLD AGENT COMPARISON RESULTS")
	lines.append("EXPERIMENT CONFIGURATION:")
	lines.append(f"Grid Size: {config['grid_size']}x{config['grid_size']}")
	lines.append(f"Number of Wumpus: {config['num_wumpus']}")
	lines.append(f"Pit Density: {config['pit_density']}")
	lines.append(f"Number of Tests: {config['num_tests']}")
	lines.append(f"Test Mode: {config['mode']}")
	lines.append("")
	lines.append("DETAILED RESULTS BY TEST:")
	for i in range(config['num_tests']):
		lines.append(f"Test {i+1}:")
		lines.append(f"Smart Agent: {'WIN' if smart_results[i]['won'] else 'LOSE'} | Score: {smart_results[i]['score']} | Moves: {smart_results[i]['moves']}")
		lines.append(f"Random Agent: {'WIN' if random_results[i]['won'] else 'LOSE'} | Score: {random_results[i]['score']} | Moves: {random_results[i]['moves']}")
		lines.append("")
	lines.append("SUMMARY STATISTICS:")
	lines.append("Smart Agent (Hybrid):")
	lines.append(f"Total Tests: {config['num_tests']}")
	lines.append(f"Wins: {smart_wins}")
	lines.append(f"Win Rate: {smart_wins/config['num_tests']*100:.1f}%")
	lines.append(f"Average Score: {smart_avg_score:.2f}")
	lines.append(f"Average Moves: {smart_avg_moves:.2f}")
	lines.append("")
	lines.append("Random Agent (Baseline):")
	lines.append(f"Total Tests: {config['num_tests']}")
	lines.append(f"Wins: {random_wins}")
	lines.append(f"Win Rate: {random_wins/config['num_tests']*100:.1f}%")
	lines.append(f"Average Score: {random_avg_score:.2f}")
	lines.append(f"Average Moves: {random_avg_moves:.2f}")
	lines.append("")
	lines.append("CONCLUSION:")
	lines.append(f"Smart Agent outperforms Random Agent by {(smart_wins-random_wins)/config['num_tests']*100:.1f} percentage points.")
	output_dir = "Output"
	os.makedirs(output_dir, exist_ok=True)
	output_file = os.path.join(output_dir, "resultComparison.txt")
	with open(output_file, 'w', encoding='utf-8') as f:
		f.write("\n".join(lines))
	print(f"✅ Results saved to: {output_file}")
