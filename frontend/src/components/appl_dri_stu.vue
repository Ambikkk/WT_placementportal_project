<script setup>
const props=defineProps(['drive'])
</script>
<template>
    <tr :key="props.drive.id">
        <td>{{props.drive.name}}</td>
        <td>{{props.drive.company}}</td>
        <td>{{props.drive.date}}</td>
        <td><button class="btn btn-primary btn-sm">View</button></td>
    </tr>
</template>