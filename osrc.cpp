/* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
 * osrc.cpp version 0.1 (2018-01-13 rev #01)                                             *
 * A search program for low-period oscillators and "short-wide" spaceships,              *
 *  written in cross-platform C++.                                                       *
 * It probably could just be in C, but I don't know much C so I didn't want to go there. *
 *                                                                                       *
 * Options:                                                                              *
 *                                                                                       *
 *     PERIOD:          Sets the period of the search (from 1 to 10, or higher prime     *
 *                       periods). Higher composite periods supported incompletely.      *
 *                                                                                       *
 *     WIDTH:           Sets the width of the search (from 1 to 9).                      *
 *                                                                                       *
 *                       WARNING: A width-9 search uses slightly over 2 GB. A width-8    *
 *                                search uses approximately 270 MB. Width-10 searches    *
 *                                are possible in principle, but likely require at least *
 *                                17 GB available. Memory usage may be reduced in future *
 *                                versions.                                              *
 *                                                                                       *
 *     MAX_LENGTH:      Sets the maximum length of the search.                           *
 *                                                                                       *
 *     FULL_PD_BY:      Requires all partials to have their first full-period row by     *
 *                       this length.                                                    *
 *                                                                                       *
 *     MIN_ROTOR_WIDTH: Requires all solutions to have at least this many rows between   *
 *                       their first and last full-period rows (inclusive).              *
 *                                                                                       *
 *     MAX_SOLUTIONS:   After this many solutions have been found, stop search.          *
 *                                                                                       *
 *     SYMMETRY:        Asymmetric, odd, even, and gutter modes supported.               *
 *                                                                                       *
 *     SHIFT:           Allows searches for c/n spaceships by offsetting the first       *
 *                       generation and last generation by 1 relative to each other.     *
 *                                                                                       *
 *                                                                                       *
 * Known limitations:                                                                    *
 *                                                                                       *
 *     Full-period testing for composite periods is incomplete.                          *
 *                                                                                       *
 *     Extremely high memory usage for relatively high widths.                           *
 *                                                                                       *
 *     Requires a moderate degree of effort and ntzfind-setup.cpp to change the rule.    *
 *                                             (from an old version of ntzfind)          *
 *                                                                                       *
 *     Changes to the source code and recompilation are required to change the search    *
 *      settings.                                                                        *
 *                                                                                       *
 *     Much slower than zfind for equivalent periods and widths.                         *
 *                                                                                       *
 *     Does no stator optimization, and only rudimentary support for eliminating         *
 *      duplicate-rotor solutions. Outputs each solution in every phase once per phase.  *
 *                                                                                       *
 *     This comment box is very difficult to format.                                     *
 *                                                                                       *
 * By Aidan F. Pierce and whoever else wants to get rid of any of the above limitations  *
 *  and/or add new functionality.                                                        *
 * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * */

#include <iostream>
#include <string>
//* Get rid of the first / if you've figured out how to accept command-line parameters and autogenerate this part into a file called settings.cpp.
//Don't change things here:
#define SYM false
#define GAP 0
#define NONE 0
#define GUTTER 1
#define ODD 2
#define EVEN 3

//Change things here:
#define PERIOD 3
#define WIDTH 6
#define MAX_LENGTH 50 //Not guaranteed to be exact
#define FULL_PD_BY 1 //Do not set this to zero
#define MIN_ROTOR_WIDTH 0
#define MAX_SOLUTIONS 0x7FFFFFFF
#define SYMMETRY NONE //NONE, GUTTER, ODD, EVEN
//Uncomment this to search for c/PERIOD spaceships instead. The SYMMETRY option will be ignored.
#define SHIFT

//Don't change things here:
//For that matter, don't pay attention to the awful parameter names either.
#ifdef SHIFT
#define SYMMETRY NONE
#endif

#if SYMMETRY == GUTTER
#undef SYM //Avoid pointless warning
#define SYM true
#elif SYMMETRY == ODD
#undef GAP //Avoid another pointless warning
#define GAP 2
#elif SYMMETRY == EVEN
#undef GAP //Avoid yet another pointless warning
#define GAP 1
#endif

//Change this if you dare (at least to any rule with B3i and without B2a, B2c, or B1e):			 P.S. Don't bother even thinking about B0 or B1c rules.
//Randomly copied from ntzfind (B3/S23). If you have ntzfind (at least the older version), it's fairly simple to generate one of these for any rule you want.
int stepcell(int o, int a, int b, int c, int d, int e, int f, int g, int h){
	return (~o&((0x0)|((a^b^c^d^e^f^g^h)&(((a|b|c|d)&(e|f|g|h))|((a|b|e|f)&(c|d|g|h)))&~(((a|b)&(c|d)&(e|f)&(g|h))|(~((a&b)^(c&d)^(e&f)^(g&h))&((a&b)|(c&d)|(e&f)|(g&h)))))))|(o&((0x0)|(~(a^b^c^d^e^f^g^h)&(a|b|c|d|e|f|g|h)&~(((a|b|c)&(d|e|f)&(g|h))|(a&b&c)|(d&e&f)|((a|b|c)&(d|e|f)&(~(a^b^c)|~(d^e^f)))|(g&h&(a|b|c|d|e|f))))|((a^b^c^d^e^f^g^h)&(((a|b|c|d)&(e|f|g|h))|((a|b|e|f)&(c|d|g|h)))&~(((a|b)&(c|d)&(e|f)&(g|h))|(~((a&b)^(c&d)^(e&f)^(g&h))&((a&b)|(c&d)|(e&f)|(g&h)))))));
}
//tlife: return (~o&((0x0)|((a^b^c^d^e^f^g^h)&(((a|b|c|d)&(e|f|g|h))|((a|b|e|f)&(c|d|g|h)))&~(((a|b)&(c|d)&(e|f)&(g|h))|(~((a&b)^(c&d)^(e&f)^(g&h))&((a&b)|(c&d)|(e&f)|(g&h)))))))|(o&((0x0)|(~(a^b^c^d^e^f^g^h)&(a|b|c|d|e|f|g|h)&~(((a|b|c)&(d|e|f)&(g|h))|(a&b&c)|(d&e&f)|((a|b|c)&(d|e|f)&(~(a^b^c)|~(d^e^f)))|(g&h&(a|b|c|d|e|f)))&~(~(b|d|f|h)&~((a^e)|(c^g))))|((a^b^c^d^e^f^g^h)&(((a|b|c|d)&(e|f|g|h))|((a|b|e|f)&(c|d|g|h)))&~(((a|b)&(c|d)&(e|f)&(g|h))|(~((a&b)^(c&d)^(e&f)^(g&h))&((a&b)|(c&d)|(e&f)|(g&h)))))|(0x0|(((~b&~f)&~((~c^~e)|(~a^~g))&(~e^~g)&~(~d|~h))|((~d&~h)&~((~e^~g)|(~a^~c))&(~c^~e)&~(~b|~f))))));
//B3/S23: return (~o&((0x0)|((a^b^c^d^e^f^g^h)&(((a|b|c|d)&(e|f|g|h))|((a|b|e|f)&(c|d|g|h)))&~(((a|b)&(c|d)&(e|f)&(g|h))|(~((a&b)^(c&d)^(e&f)^(g&h))&((a&b)|(c&d)|(e&f)|(g&h)))))))|(o&((0x0)|(~(a^b^c^d^e^f^g^h)&(a|b|c|d|e|f|g|h)&~(((a|b|c)&(d|e|f)&(g|h))|(a&b&c)|(d&e&f)|((a|b|c)&(d|e|f)&(~(a^b^c)|~(d^e^f)))|(g&h&(a|b|c|d|e|f))))|((a^b^c^d^e^f^g^h)&(((a|b|c|d)&(e|f|g|h))|((a|b|e|f)&(c|d|g|h)))&~(((a|b)&(c|d)&(e|f)&(g|h))|(~((a&b)^(c&d)^(e&f)^(g&h))&((a&b)|(c&d)|(e&f)|(g&h)))))));


//*/#include "settings.cpp"
inline int steprow(int r1, int r2, int r3){
	return stepcell(r2, r1, r1 >> 1 | (((r1 >> (WIDTH-GAP)) & 1) << (WIDTH-1)), r2 >> 1 | (((r2 >> (WIDTH-GAP)) & 1) << (WIDTH-1)), r3 >> 1 | (((r3 >> (WIDTH-GAP)) & 1) << (WIDTH-1)), r3, r3 << 1, r2 << 1, r1 << 1) & ((1 << WIDTH) - 1); //It's magic. Don't ask. So is the last function.
}//The search state
int rows[MAX_LENGTH][PERIOD];
//Search metadata for lookup in table_of_tables
int rind[MAX_LENGTH][PERIOD];
//Holds counts of possible matching extensions to combinations of rows
int main_table[1<<(WIDTH*3)];
//Holds the extensions themselves
int* table_of_tables[1<<(WIDTH*3)];
#define LMASK 1<<(WIDTH-1)
#define RMASK 1
#define RNULL 1<<WIDTH
void make_tables(){
	long r1, r2, r3, r4, ind;
	int* temp; //Pointless, on second thought, but I don't feel like fixing it now.
	//Initialize counts to 0
	for(long long i = 0; i < 1<<(WIDTH*3); i++){
		main_table[i] = 0;
		table_of_tables[i] = nullptr;
	}
	//Generate counts
	for(long long i = 0; i < 1<<(WIDTH*3); i++){
		r1 = i >> (WIDTH*2); //Top row
		r2 = (i >> WIDTH) & ((1 << WIDTH) - 1); //Middle row
		r3 = i & ((1 << WIDTH) - 1); //Bottom row
		r4 = steprow(r1, r2, r3); //Result
		//Check edge cases:				  !NOTE! This only works in rules with B3i and none of B1e, B2a, and B2c.
		if(!(!GAP && (r1 & r2 & r3 & LMASK)) && !(!SYM && (r1 & r2 & r3 & RMASK))){
			main_table[r1 << (WIDTH*2) | r2 << WIDTH  | r4]++; //Increment extension count for r124 combo
		}
	}
	
	//Do all that again to populate the extension table
	for(long long i = 0; i < 1<<(WIDTH*3); i++){
		r1 = i >> (WIDTH*2); //Top row
		r2 = (i >> WIDTH) & ((1 << WIDTH) - 1); //Middle row
		r3 = i & ((1 << WIDTH) - 1); //Bottom row
		r4 = steprow(r1, r2, r3); //Result
		ind = r1 << (WIDTH*2) | r2 << WIDTH  | r4; //Index in count, extension tables
		//Check edge cases:				  !NOTE! This only works in rules with B3i and none of B1e, B2a, and B2c.
		if(!(!GAP && (r1 & r2 & r3 & LMASK)) && !(!SYM && (r1 & r2 & r3 & RMASK))){
			//Populate table of extensions
			if(table_of_tables[ind] == nullptr){
				table_of_tables[ind] = new int[main_table[ind]+1];//Add 1 for null-terminated array
				table_of_tables[ind][0] = RNULL;
			}
			//Find first unfilled index with SNEAKY POINTER MATH!!!
			//I'm exaggerating; it's not that interesting. It's quite useless, in fact, and less safe than it could be.
			for(temp = table_of_tables[ind]; *temp != RNULL; temp++);
			*temp = r3;
			//Null-terminate it!
			*(temp+1) = RNULL;
		}
	}
}

//Main search subroutines start here.

//Convert a row of Bits inTO a plaintext String
inline std::string btos(int b){
	std::string rtn = "";
	for(int i = 0; i < WIDTH; i++){
		rtn += ((b >> i) & 1) ? 'O' : '.';
	}
	return rtn;
}
//const int subperiods[9][3] = {{1,1,1},{1,1,1},{1,1,2},{1,1,1},{1,2,3},{1,1,1},{1,2,4},{1,1,3},{1,2,5}};
int max_full_pd_length = MAX_LENGTH;
int scount = 0;

//Figure out if it's an exciting, full-period, wide-rotor solution or if it's just a boring old still life or something.
bool handle_solution(int length){
	int test = 0, q = 0;
	bool test2 = false;
	
	//Test for first full-periodic row
	for(int i = 0; i < length; i++, q+=!test2){
		test = rows[i][0];
		for(int j = 1; j < PERIOD; j++){
//There MUST be a better way.
#if PERIOD == 4
			if(j != 2) continue;
#endif
#if PERIOD == 6
			if(j != 3) continue;
#endif
#if PERIOD == 8
			if(j != 4) continue;
#endif
#if PERIOD == 9
			if(j != 3) continue;
#endif
#if PERIOD == 10
			if(j != 5) continue;
#endif
			if(rows[i][j] != test){
				test2 = true;
			}
		}
	}
	if(!test2) return false; //If there aren't any, why bother?
	
	//Test for last full-periodic row
	for(int i = length-1; i >= 0; i--){
		test = rows[i][0];
		for(int j = 1; j < PERIOD; j++){
//Here, too.
#if PERIOD == 4
			if(j != 2) continue;
#endif
#if PERIOD == 6
			if(j != 3) continue;
#endif
#if PERIOD == 8
			if(j != 4) continue;
#endif
#if PERIOD == 9
			if(j != 3) continue;
#endif
#if PERIOD == 10
			if(j != 5) continue;
#endif
			if(rows[i][j] != test){
				test2 = false;
				max_full_pd_length = i;
				break;
			}
		}
		if(!test2){
			break;
		}
	}
	
	//Minus 1 for "inclusive".
	if(max_full_pd_length - q < MIN_ROTOR_WIDTH - 1){
		return false;
	}
	
	//Yippee! It's a solution!
	scount++;
	std::cout << "Solution found (#" << scount << "); "
			  << "length = " << length-2 << ":" << std::endl; //A patent falsehood, but oh well.
	//Output it in plaintext
	for(int i = 0; i < length; i++){
		for(int j = 0; j < PERIOD; j++){
			std::cout << btos(rows[i][j]) << " ";
		}
		std::cout << "\n";
	}
	std::cout << std::endl;
	return true;
}

//Basically what it says.
inline bool test_full_pd(int length){
	int test = 0;
	bool test2 = false;
#if PERIOD > 3 && PERIOD != 5 && PERIOD != 7 && PERIOD < 11
	bool test3 = false;
#endif
	for(int i = 0; i < length; i++){
		test = rows[i][0];
#if PERIOD > 3 && PERIOD != 5 && PERIOD != 7 && PERIOD < 11
		test2 = true;
#endif
		for(int j = 1; j < PERIOD; j++){
//And here. Did I mention here?
#if PERIOD == 4
			if(j != 2) continue;
			test3 = true;
			for(int k = 0; k < PERIOD - j; k++){
				if(rows[i][j+k] != rows[i][k]){
					test3 = false;
				}
			}
			if(test3) test2 = false;
#elif PERIOD == 6
			if(j != 2 && j != 3) continue;
			test3 = true;
			for(int k = 0; k < PERIOD - j; k++){
				if(rows[i][j+k] != rows[i][k]){
					test3 = false;
				}
			}
			if(test3) test2 = false;
#elif PERIOD == 8
			if(j != 4) continue;
			test3 = true;
			for(int k = 0; k < PERIOD - j; k++){
				if(rows[i][j+k] != rows[i][k]){
					test3 = false;
				}
			}
			if(test3) test2 = false;
#elif PERIOD == 9
			if(j != 3) continue;
			test3 = true;
			for(int k = 0; k < PERIOD - j; k++){
				if(rows[i][j+k] != rows[i][k]){
					test3 = false;
				}
			}
			if(test3) test2 = false;
#elif PERIOD == 10
			if(j != 2 && j != 5) continue;
			test3 = true;
			for(int k = 0; k < PERIOD - j; k++){
				if(rows[i][j+k] != rows[i][k]){
					test3 = false;
				}
			}
			if(test3) test2 = false;
#else
			if(rows[i][j] != test){
				test2 = true;
			}
#endif
		}
		if(test2) break;
	}
	return !test2;
}

//Basically what it says.
void output_partial(int length){
	std::cout << "Partial (length = " << length << "):" << "\n";
	for(int i = 0; i < length; i++){
		for(int j = 0; j < PERIOD; j++){
			std::cout << btos(rows[i][j]) << " ";
		}
		std::cout << "\n";
	}
	std::cout << "\n";
}

//Do everything.
int main(){
	int length = 2, phase = 0, max_partial_length = 0;
	long long prev = 0; //Lookup key for the previous two rows, or at least the relevant rowphases within them.
	bool thing = false;
	make_tables();
	//Initialize search space (may or may not be necessary).
	for(int i = 0; i < MAX_LENGTH; i++){
		for(int j = 0; j < PERIOD; j++){
			rows[i][j] = 0;
			rind[i][j] = 0;
		}
	}
	/*//Some tricks to extend partial results (in this case used for finding sparkers)
	rows[0][0] = 64<<2;
	//rows[1][3] = 16<<2;
	rows[1][2] = 96<<2;
	output_partial(4);
	//*/
	//Main loop
	for(;;){//It's infinite!!!
		//handle_solution(MAX_LENGTH);
		beginning_of_infinite_loop: //This irritating language doesn't allow continues for outer loops
		//std::cout << "Q";
		//std::cout << length << " " << phase << "\n";
		if(length > 5+max_partial_length){//If search has advanced significantly
			output_partial(length);//I guess I'll comment this
			//std::cout << length;
			max_partial_length = length;//Reset expectations
		}//endif
		if(length < max_partial_length-10){//If search has shortened significantly
			max_partial_length = length;//Reset expectations
		}//endif
		if(length < 2) break; //Search complete
		rind[length][phase]++; //Advance
#ifdef SHIFT //If we're searching for spaceships
		if(phase == 1 && rows[length][0] & 1){//If there's a cell out of range, trim search to avoid segfaults
			phase--; //Backtrack in time
			if(phase < 0){ //If this is impossible
				length--; //Backtrack in space
				phase = PERIOD-1; //Return to the end of time
			} //Endif
			continue; //Nothing more to do here
		} //Endif
		prev = (rows[length-2][phase] << (2*WIDTH)) + (rows[length-1][phase] << WIDTH) + (rows[length-1][(phase+1)%PERIOD] >> (phase == PERIOD-1)); //Store lookup key
#else //If not
		prev = (rows[length-2][phase] << (2*WIDTH)) + (rows[length-1][phase] << WIDTH) + rows[length-1][(phase+1)%PERIOD]; //Store lookup key
#endif //Endelse
		//std::cout << rind[length][phase] << " " << main_table[prev] << "\n";
		if(rind[length][phase] >= main_table[prev] || length > MAX_LENGTH-2 || ((length == FULL_PD_BY + 2) && test_full_pd(length))){ //If options exhausted for current rowphase, or search otherwise needs to be pruned
			phase--; //Backtrack in time
			if(phase < 0){ //If this is impossible
				length--; //Backtrack in space
				phase = PERIOD-1; //Return to the end of time
			} //Endif
			continue; //Nothing more to do here
		} //Endif
		//std::cout << "R";
		rows[length][phase] = table_of_tables[prev][rind[length][phase]]; //Advance the current rowphase to the next option
		phase++; //Time moves forwards unless otherwise noted (above or below)
		if(phase == PERIOD){ //The universe has already ended
			length++; //Advance in space
			phase = 0; //Reset to beginning of time
			rind[length][phase] = -1; //Be sneaky and account for the annoying increment at the beginning of the loop -- this is one advantage to using signed integers.
			if(length == MAX_LENGTH) break; //Sanity check: somehow our check above for MAX_LENGTH being approached failed, so we better quit so as not to segfault.
		} else { //TMC: Too Many Comments
			rind[length][phase] = -1; //Be sneaky and account for the annoying increment at the beginning of the loop -- this is one advantage to using signed integers.
			continue; //Help with solution handling at beginning of search
		} //Endelse
		for(int i = 0; i < PERIOD; i++){ //Iterate over all generations of the previous two rows
			//std::cout << rows[length-1][phase] << " " << rows[length-2][phase] << "\n";
			if(rows[length-1][i] || rows[length-2][i]){ //If they're non-empty
				goto beginning_of_infinite_loop; //Never mind, not a solution; nothing to see here, move along
			} //Endif
		} //Endfor
		//Yay, it works!
		//std::cout << length << " ";
		thing = handle_solution(length); //They dissolve quite well, actually (at least in sulfuric acid)
		if(scount > MAX_SOLUTIONS) break; //TMS: Too Many Solutions
		//std::cout << length << " ";
		if(!thing) output_partial(length); //If it is, in fact, nothing, output it anyways, but no false advertising it as a solution
		length = ((max_full_pd_length!=MAX_LENGTH) ? max_full_pd_length : (length-2)); //Skips a few things, but oh well.
		//std::cout << length << " " << max_full_pd_length;
		phase = PERIOD-1; //Return to the end of time again
	}//End the infinite loop
	std::cout << "Search complete: " << scount << " solution" << (scount == 1 ? "" : "s") << " found.";
	/*
	for(int i = 0; i < 1 << (WIDTH*3); i++){
		std::cout << "\n" << i << "\n" << main_table[i] << "\n";
		for(int j = 0; j < main_table[i]; j++){
			std::cout << table_of_tables[i][j] << "\n";
		}
	}//*/
	
	std::cout << std::endl; //Just because.
	return 0;
}