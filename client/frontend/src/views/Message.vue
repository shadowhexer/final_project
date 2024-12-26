<script setup lang="ts">
import { onMounted, ref } from 'vue';
import API from '@/services/api';

const formPush = ref({
  message: '',
  author: 'Hexer',
});

const outputGrade = ref({
  author: '',
  message: '',
});

const received = ref<{ reference_key: string; key: string; iv: string }[]>([]);

const submit = async () => {
  try {
    const response = await API.post('sent/', JSON.stringify(formPush.value));
    if (response.status === 200) {
      received.value = response.data;
      console.log('Value received:', received.value);
      await fetch();
    }
  } catch (error) {
    alert('Error submitting form: ' + error);
  }
};

const fetch = async () => {
  try {
    const response = await API.post('message/', JSON.stringify(received.value));
    if (response.status == 200) {
      outputGrade.value.author = response.data.author;
      outputGrade.value.message = response.data.message;
      console.log('Value received:', outputGrade.value);
    }
  } catch (error) {
    console.error('Error fetching messages:', error);
  }
};
</script>

<template>
  <v-responsive>
    <v-app hidden >
      <v-card width="500" height="100%">


        
        <v-form class="d-flex flex-row" @submit.prevent="submit">
          <v-text-field v-model="formPush.message" label="Input something..." :counter="20" maxLength="20"
            variant="outlined" class="mr-4" />
          <v-btn type="submit" height="55" class="rounded-0">
            Submit
          </v-btn>
        </v-form>

        
          
      </v-card>

    </v-app>
  </v-responsive>

</template>

<style scoped>
</style>
