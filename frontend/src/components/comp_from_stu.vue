<script setup>
    const props=defineProps(['company'])
 </script>
<template>
    <li :key="props.company.id" class="list-group-item d-flex justify-content-between">
        {{props.company.name}}<button class="btn btn-info btn-sm">View</button>
    </li>
</template>