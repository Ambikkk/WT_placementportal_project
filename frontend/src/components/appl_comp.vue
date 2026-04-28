<script setup>
const props=defineProps(['student'])
</script>
<template>
    <ul :key="props.student.id" class="list-group list-group-flush">
        <li class="list-group-item d-flex justify-content-between">
           {{props.student.name}} <button class="btn btn-primary btn-sm">Review</button>
        </li>
    </ul>
</template>