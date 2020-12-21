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