<script setup>
defineProps({
  app: Object
})
</script>

<template>
<tr>
  <td>{{ app.student_name }}</td>
  <td>{{ app.job_title }}</td>
  <td>
    <span class="badge bg-info">
      {{ app.status }}
    </span>
  </td>
</tr>
</template>