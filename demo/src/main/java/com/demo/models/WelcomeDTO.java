package com.demo.models;

public class WelcomeDTO {
    private String message;
    public WelcomeDTO(String message) {
        this.message = message;
    }

    // Getters y Setters
    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
