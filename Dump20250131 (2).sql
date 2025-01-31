-- MySQL dump 10.13  Distrib 8.0.40, for Win64 (x86_64)
--
-- Host: localhost    Database: mcm_trip_ticket
-- ------------------------------------------------------
-- Server version	8.0.40

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts` (
  `UserID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(45) NOT NULL,
  `Email` varchar(45) NOT NULL,
  `Password` varchar(45) NOT NULL,
  `Is_admin` tinyint unsigned DEFAULT NULL,
  PRIMARY KEY (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts`
--

LOCK TABLES `accounts` WRITE;
/*!40000 ALTER TABLE `accounts` DISABLE KEYS */;
INSERT INTO `accounts` VALUES (1,'Rhodessa Cascaro','rjcascaro@mcm.edu.ph','sample',0),(2,'Mico Barrios','rmBarrios@mcm.edu.ph','sample',0),(3,'Dummy','dummy@mcm.edu.ph','sample',0),(5,'Admin','admin@mcm.edu.ph','sample',1);
/*!40000 ALTER TABLE `accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mcm_listvehicles`
--

DROP TABLE IF EXISTS `mcm_listvehicles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mcm_listvehicles` (
  `VehicleID` int NOT NULL AUTO_INCREMENT,
  `VehicleName` varchar(45) DEFAULT NULL,
  `VehicleQuantity` varchar(45) DEFAULT NULL,
  `VehicleSeatingCapacity` int DEFAULT NULL,
  `VehicleImage` mediumblob,
  PRIMARY KEY (`VehicleID`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mcm_listvehicles`
--

LOCK TABLES `mcm_listvehicles` WRITE;
/*!40000 ALTER TABLE `mcm_listvehicles` DISABLE KEYS */;
/*!40000 ALTER TABLE `mcm_listvehicles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mcm_ticketform`
--

DROP TABLE IF EXISTS `mcm_ticketform`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mcm_ticketform` (
  `FormID` int NOT NULL AUTO_INCREMENT,
  `UserID` int NOT NULL,
  `DateFilled` date DEFAULT NULL,
  `RequestedBy` varchar(45) DEFAULT NULL,
  `Department` varchar(45) DEFAULT NULL,
  `Purpose_Of_Trip` varchar(300) DEFAULT NULL,
  `VehicleType` varchar(45) DEFAULT NULL,
  `Approval` tinyint DEFAULT '0',
  `Remarks` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`FormID`),
  KEY `mcm_account_ticketform_idx` (`UserID`),
  CONSTRAINT `mcm_account_ticketform` FOREIGN KEY (`UserID`) REFERENCES `accounts` (`UserID`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mcm_ticketform`
--

LOCK TABLES `mcm_ticketform` WRITE;
/*!40000 ALTER TABLE `mcm_ticketform` DISABLE KEYS */;
/*!40000 ALTER TABLE `mcm_ticketform` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `mcm_ticketform_AFTER_UPDATE` AFTER UPDATE ON `mcm_ticketform` FOR EACH ROW BEGIN
DECLARE last_start_date DATE;

    -- Check if Approval is 1
    IF NEW.Approval = 1 THEN
        -- Get the last StartDate for the given FormID
        SELECT MAX(STR_TO_DATE(StartDate, '%Y-%m-%d')) INTO last_start_date
        FROM mcm_traveldetails
        WHERE FormID = NEW.FormID;

        -- Check if the last StartDate has passed
        IF last_start_date < CURDATE() THEN
            -- Update VehicleIsUsed to 0 in mcm_vehicles
            UPDATE mcm_vehicles
            SET VehicleIsUsed = 0
            WHERE ID = (SELECT VehicleID FROM mem_ticketform WHERE FormID = NEW.FormID);
        END IF;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `mcm_traveldetails`
--

DROP TABLE IF EXISTS `mcm_traveldetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mcm_traveldetails` (
  `TravelID` int NOT NULL AUTO_INCREMENT,
  `FormID` int NOT NULL,
  `UserID` int NOT NULL,
  `StartDate` varchar(300) DEFAULT NULL,
  `StartTime` varchar(300) DEFAULT NULL,
  `EstimatedReturns` varchar(300) DEFAULT NULL,
  `Destinations` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`TravelID`),
  KEY `mcm_account_traveldetails_idx` (`UserID`),
  KEY `mcm_ticketform_idx` (`FormID`),
  CONSTRAINT `mcm_account_traveldetails` FOREIGN KEY (`UserID`) REFERENCES `accounts` (`UserID`),
  CONSTRAINT `mcm_ticketform` FOREIGN KEY (`FormID`) REFERENCES `mcm_ticketform` (`FormID`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mcm_traveldetails`
--

LOCK TABLES `mcm_traveldetails` WRITE;
/*!40000 ALTER TABLE `mcm_traveldetails` DISABLE KEYS */;
/*!40000 ALTER TABLE `mcm_traveldetails` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mcm_vehicledetails`
--

DROP TABLE IF EXISTS `mcm_vehicledetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mcm_vehicledetails` (
  `VehicleDetailsID` int NOT NULL AUTO_INCREMENT,
  `FormID` int DEFAULT NULL,
  `TravelID` int DEFAULT NULL,
  `VehicleID` int DEFAULT NULL,
  `VehicleName` varchar(45) DEFAULT NULL,
  `VehicleQuantity` int DEFAULT NULL,
  `VehicleDriver` varchar(45) DEFAULT NULL,
  `VehiclePlateNumber` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`VehicleDetailsID`),
  KEY `mcm_ticketformID_idx` (`FormID`),
  KEY `mcm_vehicleName` (`VehicleName`) /*!80000 INVISIBLE */,
  KEY `mcm_vehicleDriver` (`VehicleDriver`) /*!80000 INVISIBLE */,
  KEY `mcm_vehiclePlateNumber` (`VehiclePlateNumber`),
  KEY `mcm_travelID_idx` (`TravelID`),
  CONSTRAINT `mcm_ticketformID` FOREIGN KEY (`FormID`) REFERENCES `mcm_ticketform` (`FormID`),
  CONSTRAINT `mcm_travelID` FOREIGN KEY (`TravelID`) REFERENCES `mcm_traveldetails` (`TravelID`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mcm_vehicledetails`
--

LOCK TABLES `mcm_vehicledetails` WRITE;
/*!40000 ALTER TABLE `mcm_vehicledetails` DISABLE KEYS */;
/*!40000 ALTER TABLE `mcm_vehicledetails` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mcm_vehicles`
--

DROP TABLE IF EXISTS `mcm_vehicles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mcm_vehicles` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `VehicleID` int DEFAULT NULL,
  `VehicleName` varchar(45) DEFAULT NULL,
  `VehicleDriver` varchar(45) DEFAULT NULL,
  `VehiclePlateNumber` varchar(45) DEFAULT NULL,
  `VehicleImage` mediumblob,
  `VehicleIsUsed` tinyint DEFAULT '0',
  PRIMARY KEY (`ID`),
  KEY `VehicleID_idx` (`VehicleID`),
  KEY `VehiclePlateNumber_idx` (`VehiclePlateNumber`) /*!80000 INVISIBLE */,
  KEY `VehicleDriver` (`VehicleDriver`),
  CONSTRAINT `VehicleID` FOREIGN KEY (`VehicleID`) REFERENCES `mcm_listvehicles` (`VehicleID`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mcm_vehicles`
--

LOCK TABLES `mcm_vehicles` WRITE;
/*!40000 ALTER TABLE `mcm_vehicles` DISABLE KEYS */;
/*!40000 ALTER TABLE `mcm_vehicles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `own_ticketform`
--

DROP TABLE IF EXISTS `own_ticketform`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `own_ticketform` (
  `FormID` int NOT NULL AUTO_INCREMENT,
  `UserID` int DEFAULT NULL,
  `DateFilled` date DEFAULT NULL,
  `RequestedBy` varchar(45) DEFAULT NULL,
  `Department` varchar(45) DEFAULT NULL,
  `Purpose_Of_Trip` varchar(300) DEFAULT NULL,
  `VehicleType` varchar(45) DEFAULT NULL,
  `VehicleName` varchar(45) DEFAULT NULL,
  `Classification` varchar(45) DEFAULT NULL,
  `SeatingCapacity` varchar(45) DEFAULT NULL,
  `PlateNumber` varchar(45) DEFAULT NULL,
  `Approval` tinyint DEFAULT '0',
  `Remarks` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`FormID`),
  KEY `account_userID_idx` (`UserID`),
  KEY `account_userID_own_idx` (`UserID`),
  CONSTRAINT `account_userID_own` FOREIGN KEY (`UserID`) REFERENCES `accounts` (`UserID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=62 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `own_ticketform`
--

LOCK TABLES `own_ticketform` WRITE;
/*!40000 ALTER TABLE `own_ticketform` DISABLE KEYS */;
/*!40000 ALTER TABLE `own_ticketform` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `own_traveldetails`
--

DROP TABLE IF EXISTS `own_traveldetails`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `own_traveldetails` (
  `TravelID` int NOT NULL AUTO_INCREMENT,
  `FormID` int NOT NULL,
  `UserID` int NOT NULL,
  `StartDate` varchar(300) DEFAULT NULL,
  `StartTime` varchar(300) DEFAULT NULL,
  `EstimatedReturns` varchar(300) DEFAULT NULL,
  `Destinations` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`TravelID`),
  KEY `own_formID_idx` (`FormID`),
  KEY `account_travel-details_own_idx` (`UserID`),
  CONSTRAINT `account_travel-details_own` FOREIGN KEY (`UserID`) REFERENCES `accounts` (`UserID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `own_formID` FOREIGN KEY (`FormID`) REFERENCES `own_ticketform` (`FormID`)
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `own_traveldetails`
--

LOCK TABLES `own_traveldetails` WRITE;
/*!40000 ALTER TABLE `own_traveldetails` DISABLE KEYS */;
/*!40000 ALTER TABLE `own_traveldetails` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-01-31 11:04:17
