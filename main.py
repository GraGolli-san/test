        # # マップ名取得
        # map_name = world.get_map().name
        # print(map_name)
        # # 全walker_actor取得
        # all_walker_actors = []
        # for actor in  world.get_actors():
        #     if ("walker.pedestrian." in actor.type_id):
        #         # print(actor)
        #         all_walker_actors.append(actor)
        # # ファイルポインタの作成
        # dirname = f'{map_name}_WalkerRoute'
        # os.makedirs(dirname, exist_ok=True)
        # file_pointers = []
        # for i in range(len(all_walker_actors)):
        #     filename = "%s\\w%06d.txt" % (dirname, i)
        #     print(filename)
        #     file_pointers.append(open(filename,mode='w'))

        wroute = WalkerRoute(world, settings.fixed_delta_seconds)
        wroute.init_save()

        cnt = 0
        cnt_end = 5 * 60 / settings.fixed_delta_seconds
        while True:
            if args.sync and synchronous_master:
                world.tick()
                # print(f"tick {cnt}")
                # # ファイルへ位置情報の書き込み
                # for i in range(len(all_walker_actors)):
                #     trans = all_walker_actors[i].get_transform()
                #     loc = trans.location
                #     rot = trans.rotation
                #     trans_str = f'{loc.x} {loc.y} {loc.z} {rot.pitch} {rot.yaw} {rot.roll}\n'
                #     file_pointers[i].write(trans_str)
                wroute.tick_save()

            else:
                world.wait_for_tick()

            cnt += 1
            if cnt >= cnt_end:
                break

        # # ファイルをクローズ
        # for fp in file_pointers:
        #     fp.close()
        del wroute
