<script setup lang="ts">
import HelloWorld from './components/HelloWorld.vue'
import { onMounted, ref } from 'vue';
import API from './services/api';

const inputGrade = ref<string>('');
const outputGrade = ref({
  author: '',
  message: ''
});
const error = ref<string | null>(null);
const dialog = ref<boolean>(false);
const received = ref<{reference_key: string; key: string; iv: string}[]>([]);

const formPush = ref({
  message: '',
  author: 'Hexer'
})


function forms() {
  const submit = async () => {
    try {
      const response = await API.post('sent/', JSON.stringify(formPush.value));
      if (response.status === 200) {
        received.value = response.data;
        console.log('Value received:', received.value)
        await fetch()
      }
    } catch (error) {
      alert('Error submitting form: ' + error);
    }
  };

  const fetch = async () => {
    try {
      const response = await API.post('message/', JSON.stringify(received.value));
      if (response.status == 200){
        outputGrade.value.author = response.data.author;
        outputGrade.value.message = response.data.message;
        
        console.log('Value received:', outputGrade.value)
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
      return null;
    }
  };

  return { submit, fetch };
}


</script>

<template>
  <header>
    <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="125" height="125" />

    <div class="wrapper">
      <HelloWorld msg="Vue + Vuetify + Django" />
    </div>
  </header>

  <v-app class="h-0 my-5">
    <v-form class="d-flex flex-row" ref="submitForm" @submit.prevent="forms().submit">
      <v-text-field bg-color="surface-variant" v-model="formPush.message" label="Input something..." :counter="20"
        maxLength="20" variant="outlined" />
      <v-btn type="submit" height="55" text="Submit" class="rounded-0" />
    </v-form>

    <v-card color="surface-variant">
      <v-card-text v-if="outputGrade" class="d-flex flex-column">
        <span class="text-subtitle-1">
          From: {{ outputGrade.author }}
        </span>
        <span class="text-subtitle-1">
          Message: {{ outputGrade.message }}
        </span>
      </v-card-text>
      <v-spacer />

    </v-card>

  </v-app>

</template>

<style scoped>
.logo {
  display: block;
  margin: 0 auto 2rem;
}
</style>
