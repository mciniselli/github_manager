# github_manager

You can use this tool to do different tasks:
 ## Mining repositories
 You can mine repositories running
 ```
 python3 main.py -f file.json -c -s 0 -e 4
 ```
 With **-f** you can specify the path of the file json containing data about the repositories to mine, with **-c** you can process conditions. 
 If you want to process only a batch of the repos, you can set start (**-s**) and end (**-e**)
 This task aims at creating the list of all repos, files, methods and conditions (you can see the files in RepoManager folder).
 First of all each repo is cloned. Then we do the checkout at the last tag (or if there is no tag we look for a branch with a name that follows the path a.b.c, where a, b and c are some numbers). If we do not find a tag/branch for the checkout, we skip the repo.
 For all the repos fulfilling the previous requirement, we create file, method and conditions objects following the gerarchy of the repo (keeping all java files).
 All this files are inside **repo_manager** folder
 We use **SrcML** to process all methods and create an XML file that helps us to parse the method. For each method we add all if conditions. `srcml_manager` class is the wrapper to SrcML.
 All files related to SrcML are inside **srcML** folder.
 `srcml_parser` is used to parse the generated code (e.g. for extracting all the methods, ..)
 We're looking for certain types of conditions that are not too complicated (you can see them if `srcml_filters` file, for example we keep **if (name == null)** but we exclude **if(name == a.toString() && b != null)**). 
 To do that we used the XML code to create a tree that represent the condition. We compare each condition with some trees representing each pattern we're interested in and we can decide if that condition follows that specific pattern. We have implemented a smart way to check conditions, see `check_if_tree_are_equal`, `equal_key` and `equal_value` in **srcml_filter** file for further details.
 After the extraction of all information from a repo, all data are saved (using `repoManager/store` file). We create a folder for each repo, containing a folder for each file, containing a folder for each method, containing a folder for each condition. We use numerical IDs for each of them, and we create some csv files that keep track of all information required. We save both java and xml code for each file, method and condition.
 All data are saved in **export** folder.
 You can also abstract the method adding **do_abstraction_during_check** (for further details see the abstraction section).
 
 ## Tokens extraction
 We can also extract the list of all tokens. The code is in `token_extraction/token_extraction` file.
 You can extract then running:
 ```
 python3 main.py --tokens -p 0_200_0_15
 ```
 With **--tokens** option you can extract tokens from each method. Sometimes there are methods that we want to exclude (e.g. too long method). We can use **-p** parameter to filter them (0_100_3_10 means that we keep only methods whose length is between 0 and 100 tokens, 3 and 10 lines). We use the XML generated by SrcML to detect the tokens (saved in **tokens.txt**).
 
 ## Analysis
 You can run
 ```
 python3 main.py --analysis -p 0_200_0_15
 ```
 to analyze the extracted repos. We use **--analysis** to do that. Sometimes there are methods that we want to exclude from the analysis (e.g. too long method). We can use **-p** parameter to filter them (0_100_3_10 means that we keep only methods whose length is between 0 and 100 tokens, 3 and 10 lines).
 In `result_analysis/analysis` you can find the code to do that
 
 ## Abstraction
 
 We use **Src2Abs** to abstract the code running
 ```
 python3 main.py --abstract -p 0_100_1_5
 ```
 With **--abstract** option we can abstract the method. Sometimes there are methods that we want to exclude (e.g. too long method). We can use **-p** parameter to filter them (0_100_3_10 means that we keep only methods whose length is between 0 and 100 tokens, 3 and 10 lines).
 The code is in `abstraction/abstraction` file. We create the **abstract.java** file containing the abstracted code and **tokens.txt** containing the tokens. We use the abstract version (and the mapping file generated by Src2Abs) to map the abstract token into the row one. In this way we can split the method into tokens (NB: the result may be different from the one obtained using **--tokens** option!)
 
 ## Export dataset to SQL
 
 We created a function to export the dataset in SQL. The schema is the following:
 ```
        CREATE TABLE IF NOT EXISTS method (
        id_repo INT NOT NULL,
        id_file INT NOT NULL,
        id_method INT NOT NULL,
        code MEDIUMTEXT NOT NULL,
        code_tokens MEDIUMTEXT NOT NULL,
        abstract_code MEDIUMTEXT NOT NULL,
        abstract_representation MEDIUMTEXT NOT NULL,
        repo_name nvarchar(256) NOT NULL,
        repo_url MEDIUMTEXT NOT NULL,
        repo_commit nvarchar(60) NOT NULL,
        file_name MEDIUMTEXT NOT NULL,
        num_methods INT NOT  NULL,
        start_method nvarchar(10) NOT NULL,
        end_method nvarchar(10) NOT NULL,
        num_tokens INT NOT NULL,
        num_lines INT NOT NULL
        );
```
You can export it by running:
```
python3 main.py -exp -p 0_100_5_15
```
With **-exp** option you can export SQL query. Sometimes there are methods that we want to exclude (e.g. too long method). We can use **-p** parameter to filter them (0_100_3_10 means that we keep only methods whose length is between 0 and 100 tokens, 3 and 10 lines).

## Fix conditions
In one of the previous version of the tool there was a bug in the condition generation (the condition ID saved was wrong) This function can fix the problem.
You can run
```
python3 main.py --fix
```

## Export mask
This function allows you to mask the whole repos. It is going to create the following 3 files:
- mask.txt with the mask part and a <z> token at the end
- masked.txt with the method without the mask (replaced by a <x> token)
- info.csv with all information about the two previous files
It used the file stored during the mining of repository to create this 3 files (in particular it reads the file, creates **BeautifulSoup** object to parse XML for method and condition. Then it uses these two files to mask the code)

## Create dataset for T5 pretraining
This function can be used to create the dataset for T5 pretraining that contains the list of all methods.
You can run:
```
python3 main.py --t5_pretrain -p 0_50_1_4
```
With **--t5_pretrain** option you can create the dataset. Sometimes there are methods that we want to exclude (e.g. too long method). We can use **-p** parameter to filter them (0_100_3_10 means that we keep only methods whose length is between 0 and 100 tokens, 3 and 10 lines).

The function contained in `dataset_creation/dataset_mining` file reads all csv containing information about repos (repo_info.csv, ..).
Then using that information it retrieves all data about methods and save in **T5_pretrain** folder the method
required for T5 pretraining. It saves also the keys.csv file containing all information about each method.
A summary containing the number of methods for each repo is saved in summary.csv file.
To avoid problem we skip all the methods that contain non printable characters
