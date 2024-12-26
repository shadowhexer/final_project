<template>
    <div>
      <h1>User Profile</h1>
      <p>Name: John Doe</p>
      <p>Email: john.doe@example.com</p>
      <!-- Add more user info or profile details here -->
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const user = ref({
    name: 'John Doe',
    email: 'john.doe@example.com'
  });
  </script>
  
  <style scoped>
  /* Add styles specific to the Profile component */
  div {
    padding: 20px;
    background-color: #f9f9f9;
  }
  </style>
  