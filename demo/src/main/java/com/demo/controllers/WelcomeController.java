package com.demo.controllers;

import java.util.logging.Logger;

public class WelcomeController {

    // ⚠ Logger mal usado con datos sensibles
    private static final Logger logger = Logger.getLogger(WelcomeController.class.getName());

    // ⚠ Hardcoded secret (clave embebida)
    private static final String DB_PASSWORD = "SuperSecreta123!";
    private static final String API_KEY = "ABC123-TOKEN-INSEGURO";

}