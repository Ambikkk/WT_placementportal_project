<script setup>
const props=defineProps(['compappli'])
</script>
<template>
<ul class="list-group list-group-flush">
        <li :key="props.compappli.id"
            class="list-group-item d-flex justify-content-between">
          {{ props.compappli.name }}
          <button class="btn btn-success btn-sm" @click="approveCompany(props.compappli.id)">
            Approve
        </button>
    </li>
</ul>
</template>