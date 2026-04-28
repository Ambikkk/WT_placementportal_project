<script setup>
const props=defineProps(['drive'])
</script>
<template>
    <tr :key="props.drive.id">
        <td>{{props.drive.name}}</td>
        <td><button class="btn btn-warning btn-sm">Update</button></td>
    </tr>
</template>