
INSERT INTO informatica_connections_details
(connection_type, connection_name, user_name, connection_string, INFORMATICA_SERVER, INFORMATICA_USER, CREATED_DATE, database_name, host_name, port_number, service_name, UPDATED_DATE)
VALUES('api', 'DataX', NULL, NULL, NULL, NULL, NULL, NULL, 'datax01.prod.bos.credorax.com', '22', NULL, NULL);

INSERT INTO informatica_connections_details
(connection_type, connection_name, user_name, connection_string, INFORMATICA_SERVER, INFORMATICA_USER, CREATED_DATE, database_name, host_name, port_number, service_name, UPDATED_DATE)
VALUES('api', 'Reuters', NULL, 'selectapi.datascope.refinitiv.com', NULL, NULL, NULL, NULL, 'selectapi.datascope.refinitiv.com', '443', NULL, NULL);

INSERT INTO informatica_connections_details
(connection_type, connection_name, user_name, connection_string, INFORMATICA_SERVER, INFORMATICA_USER, CREATED_DATE, database_name, host_name, port_number, service_name, UPDATED_DATE)
VALUES('api', 'eMail server', NULL, NULL, NULL, NULL, NULL, NULL, 'dns01.prod.bos.credorax.com', '25', NULL, NULL);

INSERT INTO informatica_connections_details
(connection_type, connection_name, user_name, connection_string, INFORMATICA_SERVER, INFORMATICA_USER, CREATED_DATE, database_name, host_name, port_number, service_name, UPDATED_DATE)
VALUES('api', 'visa verify files', NULL, NULL, NULL, NULL, NULL, NULL, 'sfile2.trusted.visa.com', '22', NULL, NULL);

INSERT INTO informatica_connections_details
(connection_type, connection_name, user_name, connection_string, INFORMATICA_SERVER, INFORMATICA_USER, CREATED_DATE, database_name, host_name, port_number, service_name, UPDATED_DATE)
VALUES('api', 'ECB', NULL, 'www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip', NULL, NULL, NULL, NULL, 'www.ecb.europa.eu', '443', NULL, NULL);

INSERT INTO informatica_connections_details
(connection_type, connection_name, user_name, connection_string, INFORMATICA_SERVER, INFORMATICA_USER, CREATED_DATE, database_name, host_name, port_number, service_name, UPDATED_DATE)
VALUES('api', 'Oanada', NULL, 'https://web-services.oanda.com/rates/api/v1/rates/', NULL, NULL, NULL, NULL, 'web-services.oanda.com', '443', NULL, NULL);

INSERT INTO informatica_connections_details
(connection_type, connection_name, user_name, connection_string, INFORMATICA_SERVER, INFORMATICA_USER, CREATED_DATE, database_name, host_name, port_number, service_name, UPDATED_DATE)
VALUES('api', 'bindb', NULL, 'https://members.bindb.com/priority-update/', NULL, NULL, NULL, NULL, 'members.bindb.com', '443', NULL, NULL);

INSERT INTO informatica_connections_details
(connection_type, connection_name, user_name, connection_string, INFORMATICA_SERVER, INFORMATICA_USER, CREATED_DATE, database_name, host_name, port_number, service_name, UPDATED_DATE)
VALUES('api', 'sg', NULL, 'https://nsg-gw-bos.credorax.com', NULL, NULL, NULL, NULL, 'nsg-gw-bos.credorax.com', '443', NULL, NULL);


INSERT INTO informatica_connections_details
(connection_type, connection_name, user_name, connection_string, INFORMATICA_SERVER, INFORMATICA_USER, CREATED_DATE, database_name, host_name, port_number, service_name, UPDATED_DATE)
VALUES('api', 'alipay', NULL, NULL, NULL, NULL, NULL, NULL, 'sftp.alipay.com', '22', NULL, NULL);


commit;
