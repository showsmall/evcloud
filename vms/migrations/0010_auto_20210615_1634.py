# Generated by Django 3.2.2 on 2021-06-15 08:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('compute', '0005_remove_host_vlans'),
        ('vms', '0009_vmarchive_host_released'),
    ]

    operations = [
        migrations.CreateModel(
            name='MigrateTask',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('vm_uuid', models.CharField(max_length=36, verbose_name='虚拟机UUID')),
                ('src_host_ipv4', models.GenericIPAddressField(verbose_name='源宿主机IP')),
                ('src_undefined', models.BooleanField(default=False, verbose_name='是否已清理源云主机')),
                ('src_is_free', models.BooleanField(default=False, verbose_name='是否释放源宿主机资源')),
                ('dst_host_ipv4', models.GenericIPAddressField(verbose_name='目标宿主机IP')),
                ('dst_is_claim', models.BooleanField(default=False, verbose_name='是否扣除目标宿主机资源')),
                ('migrate_time', models.DateTimeField(auto_now_add=True, verbose_name='迁移时间')),
                ('migrate_complete_time', models.DateTimeField(blank=True, default=None, null=True, verbose_name='迁移完成时间')),
                ('status', models.CharField(choices=[('failed', '迁移失败'), ('in-process', '正在迁移'), ('some-todo', '迁移完成，有些需要善后的工作'), ('complete', '迁移完成')], default='complete', max_length=16, verbose_name='迁移状态')),
                ('content', models.TextField(blank=True, default='', null=True, verbose_name='文字记录')),
                ('tag', models.CharField(choices=[('live', '动态迁移'), ('static', '静态迁移')], default='static', max_length=16, verbose_name='迁移类型')),
                ('dst_host', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dst_migrate_log_set', to='compute.host')),
                ('src_host', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='src_migrate_log_set', to='compute.host')),
                ('vm', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='migrate_log_set', to='vms.vm')),
            ],
            options={
                'verbose_name': '虚拟机迁移记录',
                'verbose_name_plural': '虚拟机迁移记录表',
                'ordering': ['-id'],
            },
        ),
        migrations.DeleteModel(
            name='MigrateLog',
        ),
    ]
