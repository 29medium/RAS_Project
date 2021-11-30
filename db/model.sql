-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema rasbet
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `rasbet` ;

-- -----------------------------------------------------
-- Schema rasbet
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `rasbet` DEFAULT CHARACTER SET utf8 ;
USE `rasbet` ;

-- -----------------------------------------------------
-- Table `rasbet`.`User`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rasbet`.`User` ;

CREATE TABLE IF NOT EXISTS `rasbet`.`User` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) NOT NULL,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(45) NOT NULL,
  `password` VARCHAR(45) NOT NULL,
  `iban` VARCHAR(25) NOT NULL,
  `nif` VARCHAR(9) NOT NULL,
  `cc` VARCHAR(8) NOT NULL,
  `birth_date` DATETIME NOT NULL,
  `type` INT NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `email_UNIQUE` ON `rasbet`.`User` (`email` ASC) VISIBLE;

CREATE UNIQUE INDEX `username_UNIQUE` ON `rasbet`.`User` (`username` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `rasbet`.`Odd`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rasbet`.`Odd` ;

CREATE TABLE IF NOT EXISTS `rasbet`.`Odd` (
  `id` INT NOT NULL,
  `value` DECIMAL(7,2) NOT NULL,
  `description` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `rasbet`.`Bet`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rasbet`.`Bet` ;

CREATE TABLE IF NOT EXISTS `rasbet`.`Bet` (
  `id` INT NOT NULL,
  `value` DECIMAL(7,2) NOT NULL,
  `state` INT NOT NULL,
  `User_id` INT NOT NULL,
  `Odd_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_Bet_User`
    FOREIGN KEY (`User_id`)
    REFERENCES `rasbet`.`User` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Bet_Odd1`
    FOREIGN KEY (`Odd_id`)
    REFERENCES `rasbet`.`Odd` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_Bet_User_idx` ON `rasbet`.`Bet` (`User_id` ASC) VISIBLE;

CREATE INDEX `fk_Bet_Odd1_idx` ON `rasbet`.`Bet` (`Odd_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `rasbet`.`Transaction`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rasbet`.`Transaction` ;

CREATE TABLE IF NOT EXISTS `rasbet`.`Transaction` (
  `id` INT NOT NULL,
  `value` DECIMAL(7,2) NOT NULL,
  `type` INT NOT NULL,
  `date` DATETIME NOT NULL,
  `User_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_Transaction_User1`
    FOREIGN KEY (`User_id`)
    REFERENCES `rasbet`.`User` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_Transaction_User1_idx` ON `rasbet`.`Transaction` (`User_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `rasbet`.`Event`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rasbet`.`Event` ;

CREATE TABLE IF NOT EXISTS `rasbet`.`Event` (
  `id` INT NOT NULL,
  `start_date` DATETIME NOT NULL,
  `state` INT NOT NULL,
  `Odd_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_Event_Odd1`
    FOREIGN KEY (`Odd_id`)
    REFERENCES `rasbet`.`Odd` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_Event_Odd1_idx` ON `rasbet`.`Event` (`Odd_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `rasbet`.`Competition`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rasbet`.`Competition` ;

CREATE TABLE IF NOT EXISTS `rasbet`.`Competition` (
  `id` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `description` VARCHAR(45) NULL,
  `Event_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_Competition_Event1`
    FOREIGN KEY (`Event_id`)
    REFERENCES `rasbet`.`Event` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_Competition_Event1_idx` ON `rasbet`.`Competition` (`Event_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `rasbet`.`Sport`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `rasbet`.`Sport` ;

CREATE TABLE IF NOT EXISTS `rasbet`.`Sport` (
  `id` INT NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `description` VARCHAR(45) NULL,
  `Competition_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_Sport_Competition1`
    FOREIGN KEY (`Competition_id`)
    REFERENCES `rasbet`.`Competition` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_Sport_Competition1_idx` ON `rasbet`.`Sport` (`Competition_id` ASC) VISIBLE;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
