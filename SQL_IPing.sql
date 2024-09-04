IF NOT EXISTS (SELECT name FROM master.dbo.sysdatabases WHERE name = 'DATABASE_NAME_HERE')
BEGIN
    CREATE DATABASE "DATABASE_NAME_HERE";
END;
GO

USE "DATABASE_NAME_HERE";
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Licenses')
BEGIN
    CREATE TABLE Licenses (
        guid VARCHAR(36) PRIMARY KEY NOT NULL,
        active BIT NOT NULL,
        klt_name VARCHAR (50) NOT NULL,
        expiry_date datetime ,
		klt_mail VARCHAR(45),
		imie_nazwisko VARCHAR(30),
		telefon VARCHAR(11),
		country VARCHAR(2),
		app_endpoint VARCHAR(100) NOT NULL,
		ping_endpoint VARCHAR(100) NOT NULL
    );
END;
GO

INSERT INTO Licenses(guid, active, expiry_date, klt_name, klt_mail, telefon, imie_nazwisko, country, app_endpoint, ping_endpoint) 
	VALUES ('8a36bb31-b991-4b16-8307-0945b80b2c2e', 1, '2024-12-31 00:00:00.000','Jan Kowalski - DEMO', 'kontakt@test.pl', '0','Jan Kowalski','PL','https://endpointsql.iping.pl/app_exe','https://endpointsql.iping.pl')
GO

INSERT INTO Licenses(guid, active, expiry_date, klt_name, klt_mail,telefon, imie_nazwisko, country, app_endpoint, ping_endpoint) 
	VALUES ('9672ad60-2ca6-4099-ae73-714e8a251e15', 1, '2024-12-31 00:00:00.000','DEMO1', 'radoslaw.skonieczny@gmail.com', '48602642402', 'demo 1','PL','https://endpointsql.iping.pl/app_exe','https://endpointsql.iping.pl')
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'App_lic')
BEGIN
    CREATE TABLE App_lic (
        guid VARCHAR(36)  NOT NULL,
        app_guid VARCHAR(36) PRIMARY KEY ,
		app_ver VARCHAR(2),
		alert_now BIT DEFAULT 0,
		alert_notify_mail_send BIT DEFAULT 0,
		last_seen datetime ,
		last_seen_alert datetime,
		client_description VARCHAR(60),
		public_ip VARCHAR(15),
		current_user_c VARCHAR(40),
		hostname VARCHAR(30),
		os_info VARCHAR(100),
		alert_mail_address VARCHAR(60), --email do alertów dla danego app_guid
		app_activated_license BIT NOT NULL, --rêcznie mo¿na zbanowaæ dan¹ app_guid
		SMS_alerting BIT DEFAULT 0,	--True/False czy aktywna funkcjonalnosc wysy³ki sms
		SMS_alert_number VARCHAR(11) DEFAULT '48000000000',  --numer tel do wysy³ki sms z danego app_guid
		repeat_count INT DEFAULT 30 NOT NULL,  --g³owna pêtla aby ograniczyæ odpytywania licencji
		repeat_delay INT DEFAULT 2 NOT NULL, --zw³oka czasowa pomiêdzy pingami
		ping_repeat INT DEFAULT 5 NOT NULL --ile pingów puszcza przy testach icmp
    );
END;
GO
----
INSERT INTO App_lic(guid,  alert_mail_address, app_guid, client_description, app_activated_license)
VALUES ('8a36bb31-b991-4b16-8307-0945b80b2c2e', 'kontakt@test.pl',				'd3e7e4e4-381c-4d83-9937-2aaf03f757c7', 'Ursynów', 1)

INSERT INTO App_lic(guid,  alert_mail_address, app_guid, client_description, app_activated_license)
VALUES ('8a36bb31-b991-4b16-8307-0945b80b2c2e', 'kontakt@test.pl',				'2c7bc3af-c5b7-4881-95a1-4c06d8b7da5a', 'Pu³awska', 1)

INSERT INTO App_lic(guid,  alert_mail_address, app_guid, client_description, app_activated_license)
VALUES ('8a36bb31-b991-4b16-8307-0945b80b2c2e', 'kontakt@test.pl',				'8f7aa9e2-a8d1-464c-85d0-e1d72bc16bcc', 'Kajakowa',1)
GO
-----------------------------------------------------
INSERT INTO App_lic(guid,  alert_mail_address, app_guid, client_description, app_activated_license)
VALUES ('9672ad60-2ca6-4099-ae73-714e8a251e15', 'radoslaw.skonieczny@gmail.com', 'e029855a-7bea-4bab-9c96-99406b027237', 'Warszawa',1)
GO

INSERT INTO App_lic(guid,  alert_mail_address, app_guid, client_description,app_activated_license)
VALUES ('9672ad60-2ca6-4099-ae73-714e8a251e15', 'radoslaw.skonieczny@gmail.com', 'cb190d71-8436-4543-b5cf-7d5875f364dc', 'Warszawa2',1)
GO

INSERT INTO App_lic(guid,  alert_mail_address, app_guid, client_description, app_activated_license)
VALUES ('9672ad60-2ca6-4099-ae73-714e8a251e15', 'radoslaw.skonieczny@gmail.com', '4cdf2f29-5d7b-4c81-bab2-b534678547dc', 'Szczecin',1)
GO

INSERT INTO App_lic(guid,  alert_mail_address, app_guid, client_description, app_activated_license)
VALUES ('9672ad60-2ca6-4099-ae73-714e8a251e15', 'radoslaw.skonieczny@gmail.com', '06f87bb2-248f-41c3-8172-fd6c33c8ab14', 'Warszawa',1)
GO

INSERT INTO App_lic(guid,  alert_mail_address, app_guid, client_description,app_activated_license)
VALUES ('9672ad60-2ca6-4099-ae73-714e8a251e15', 'radoslaw.skonieczny@gmail.com', 'bf592eb0-3524-46c8-babf-bdd31ca66d2a', 'Wroc³aw',1)
GO

INSERT INTO App_lic(guid,  alert_mail_address, app_guid, client_description,app_activated_license)
VALUES ('9672ad60-2ca6-4099-ae73-714e8a251e15', 'radoslaw.skonieczny@gmail.com', 'ecd770f9-a084-48a5-8734-22c9fbcd751b', '£ódŸ',1)
GO
-----------


IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Host_data_bufor')
BEGIN
    CREATE TABLE Host_data_bufor (
        id int NOT NULL IDENTITY PRIMARY KEY,
		ip VARCHAR(15),
		port VARCHAR(5),
		description VARCHAR(60),
		reachable BIT, 
		client_description VARCHAR(60),
		guid VARCHAR(36),
		app_guid VARCHAR(36),
		app_ver VARCHAR(2),
		custom1 VARCHAR(30),
		data_log DATETIME,
		alert_mail_address VARCHAR(50)
    );
END;
GO


IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Host')
BEGIN
    CREATE TABLE Host (
        id int NOT NULL IDENTITY PRIMARY KEY,
		guid VARCHAR(36),
		app_guid VARCHAR(36),
        ip VARCHAR(15),
        port VARCHAR(5),
		percent_available DECIMAL(5,2),
        description VARCHAR(60),
		custom1 VARCHAR(60),
		data_log DATETIME,
		alert_now bit default 0,
		client_description VARCHAR(60),
		alert_notify_mail_send BIT DEFAULT 0,
		app_reachable bit, 
		alert_mail_address VARCHAR(50),
        CONSTRAINT UQ_Ip_Port_Description UNIQUE (ip, port, app_guid)
    );
END;
GO

update app_lic
set SMS_alert_number = '48602642402' where app_activated_license =1 and guid='9672ad60-2ca6-4099-ae73-714e8a251e15'