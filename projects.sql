CREATE TABLE `ProjectKeyValuePairs` (
  [Key] nvarchar(255) NOT NULL,
  [Value] nvarchar(255) NOT NULL,
  [ProjectId] int NOT NULL,
  [Id] integer  NOT NULL PRIMARY KEY AUTOINCREMENT  
);
CREATE TABLE `Projects` (
  [ProjectKey] nvarchar(255) NOT NULL,
  [ProjectTitle] nvarchar(255) NOT NULL,
  [LastChange] datetime NOT NULL,
  [DisableForMe] tinyint NOT NULL,
  [Id] integer  NOT NULL PRIMARY KEY AUTOINCREMENT  
);
