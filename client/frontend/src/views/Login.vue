<template>
  <div class="flex justify-center items-center min-h-screen bg-gray-100">
    <div class="w-full sm:w-96 md:w-1/3">
      <div :class="{ 'right-panel-active': isSignUpActive }" class="relative overflow-hidden bg-white rounded-lg shadow-lg">
        
        <form @submit.prevent="onSubmit">
          <!-- Sign Up Form -->
          <div v-if="!isSignUpActive" class="p-8">
            <h1 class="text-center text-2xl font-bold mb-6">Create Account</h1>
            <div class="flex justify-center space-x-4 mb-4">
              <button class="bg-blue-500 text-white p-2 rounded-full">
                <i class="mdi mdi-facebook"></i>
              </button>
              <button class="bg-red-500 text-white p-2 rounded-full">
                <i class="mdi mdi-google"></i>
              </button>
              <button class="bg-blue-700 text-white p-2 rounded-full">
                <i class="mdi mdi-linkedin"></i>
              </button>
            </div>
            <p class="text-center text-sm mb-6">or use your email for registration</p>
            <input v-model="form.name" class="w-full p-3 mb-4 border border-gray-300 rounded-md" type="text" placeholder="Name"/>
            <input v-model="form.email" class="w-full p-3 mb-4 border border-gray-300 rounded-md" type="email" placeholder="Email"/>
            <input v-model="form.password" class="w-full p-3 mb-4 border border-gray-300 rounded-md" type="password" placeholder="Password"/>
            <button type="submit" class="w-full bg-red-500 text-white py-3 rounded-md mt-4">Sign Up</button>
          </div>

          <!-- Sign In Form -->
          <div v-if="isSignUpActive" class="p-8">
            <h1 class="text-center text-2xl font-bold mb-6">Sign In</h1>
            <div class="flex justify-center space-x-4 mb-4">
              <button class="bg-blue-500 text-white p-2 rounded-full">
                <i class="mdi mdi-facebook"></i>
              </button>
              <button class="bg-red-500 text-white p-2 rounded-full">
                <i class="mdi mdi-google"></i>
              </button>
              <button class="bg-blue-700 text-white p-2 rounded-full">
                <i class="mdi mdi-linkedin"></i>
              </button>
            </div>
            <p class="text-center text-sm mb-6">or use your account</p>
            <input v-model="form.email" class="w-full p-3 mb-4 border border-gray-300 rounded-md" type="email" placeholder="Email"/>
            <input v-model="form.password" class="w-full p-3 mb-4 border border-gray-300 rounded-md" type="password" placeholder="Password"/>
            <button type="submit" class="w-full bg-blue-500 text-white py-3 rounded-md mt-4">Sign In</button>
            <button class="w-full text-center text-sm text-blue-500 mt-2">Forgot your password?</button>
          </div>
        </form>

        <!-- Overlay -->
        <div v-if="!isSignUpActive" class="absolute inset-0 flex justify-center items-center space-x-4">
          <button @click="toggleForm" class="bg-transparent text-white p-3 border border-white rounded-full">Sign Up</button>
          <button @click="toggleForm" class="bg-transparent text-white p-3 border border-white rounded-full">Sign In</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'SignUpSignIn',
  setup() {
    const isSignUpActive = ref(false);
    const form = ref({
      name: '',
      email: '',
      password: ''
    });

    const toggleForm = () => {
      isSignUpActive.value = !isSignUpActive.value;
    };

    const onSubmit = () => {
      if (isSignUpActive.value) {
        // Handle sign-in submission
        console.log('Sign In:', form.value);
      } else {
        // Handle sign-up submission
        console.log('Sign Up:', form.value);
      }
    };

    return {
      isSignUpActive,
      form,
      toggleForm,
      onSubmit
    };
  }
});
</script>

