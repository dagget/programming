#include<vector>
#include<iostream>

std::vector<int> solution(int Value)
{
	std::vector<int> Result;

	while(Value != 0){
		int Remainder = Value % -2;
		Value = Value / -2;

		if( Remainder < 0){
			Remainder += 2;
			Value++;
		}

		Result.push_back(Remainder);
	}

	return Result;
}

int main(int argc, char *argv[])
{
	std::vector<int> res = solution(42);
	for (std::vector<int>::const_iterator i = res.begin(); i != res.end(); ++i) {
		std::cout << *i << std::endl;
	}
	
	return 0;
}
