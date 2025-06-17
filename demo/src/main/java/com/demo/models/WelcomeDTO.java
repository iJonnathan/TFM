package com.demo.models;

public class WelcomeDTO {
    private String message;
    public WelcomeDTO(String message) {
        this.message = message;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
